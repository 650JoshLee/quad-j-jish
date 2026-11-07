"""
agent.py - YOUR poker bot. This one file is a complete web server.

Run it:
    python agent.py                  # listens on port 5008
    PORT=5010 python agent.py        # or pick a port

Play a match against a baseline (three windows):
    python agent.py                                 # your bot on port 5008
    python baseline-bots/baseline_random.py         # opponent on port 5009
    python judge_engine.py                          # judge: both halves (uses those two ports)

Check that the tournament can run it:
    python -m pytest -q              # tests in test_agent.py
    ./tools/check_build.sh           # builds and smoke-tests it like the tournament

Team: quad-j. Bot: jish_5.
Independent opponent-mixture strategy; see BOT_NOTES.md.
"""
import os
import traceback

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from evaluator import card_rank, card_suit, cards_to_str, omaha_score, warmup  # handy helpers, see evaluator.py
from game import Action, AgentConfig, HandResult, Observation, Street

# Build omaha_score's lookup table now, while the server starts, instead of
# during your first decision (where it would eat into your time bank).
# Do any other slow setup (loading a model, ...) here too: the server must
# answer within 15 seconds of starting.
warmup()

# Tournament identity
PARTICIPANT = "quad-j"
AGENT_NAME = "jish_5"


# ===== YOUR CODE HERE =====

# Independent strategy: a mixture of opponent policies and a small response tree.
import math
import random
import time
from pathlib import Path
from itertools import combinations_with_replacement
import numpy as np
from numba import njit
from evaluator import _score_ranks

# Prime products uniquely encode rank multisets. The official category order
# supplies the values: trips beat straights and flushes beat full houses.
_PRIMES = np.array([2,3,5,7,11,13,17,19,23],dtype=np.int32)
_RP = _PRIMES[np.arange(36)//4]
_SB = np.array([1 << (c%4) for c in range(36)],dtype=np.int32)
_LOOKUP = np.zeros((2,23**4*19+1),dtype=np.int32)
for rs in combinations_with_replacement(range(9),5):
    if max(rs.count(r) for r in rs)>4:continue
    key=math.prod(int(_PRIMES[r]) for r in rs)
    _LOOKUP[0,key]=_score_ranks(tuple(reversed(rs)),False)
    _LOOKUP[1,key]=_score_ranks(tuple(reversed(rs)),True)
_C = np.array([[math.comb(n,k) if k<=n else 0 for k in range(6)] for n in range(36)],dtype=np.int32)

@njit
def hand_id(h):
    a=np.sort(h);v=0
    for k in range(5):v+=_C[a[k],k+1]
    return v

@njit
def score(h,b,table):
    best=0
    for x in range(4):
        for y in range(x+1,5):
            r=_RP[h[x]]*_RP[h[y]];s=_SB[h[x]]&_SB[h[y]]
            for i in range(len(b)-2):
                for j in range(i+1,len(b)-1):
                    for k in range(j+1,len(b)):
                        idx=r*_RP[b[i]]*_RP[b[j]]*_RP[b[k]]
                        flush=int((s&_SB[b[i]]&_SB[b[j]]&_SB[b[k]])!=0)
                        v=table[flush,idx]
                        if v>best:best=v
    return best

@njit
def draw(state):
    # SplitMix64, with state private to this invocation.
    state+=np.uint64(0x9e3779b97f4a7c15)
    z=state;z=(z^(z>>np.uint64(30)))*np.uint64(0xbf58476d1ce4e5b9)
    z=(z^(z>>np.uint64(27)))*np.uint64(0x94d049bb133111eb)
    return state,int((z^(z>>np.uint64(31)))%np.uint64(36))

@njit
def equity_trials(h,trials,seed,table):
    state=np.uint64(seed);mask=np.uint64(0);win=0.
    for c in h:mask|=np.uint64(1)<<np.uint64(c)
    other=np.empty(5,np.int32);board=np.empty(5,np.int32)
    for n in range(trials):
        used=mask
        for k in range(10):
            while True:
                state,c=draw(state);bit=np.uint64(1)<<np.uint64(c)
                if not (used&bit):break
            used|=bit
            if k<5:other[k]=c
            else:board[k-5]=c
        a=score(h,board,table);b=score(other,board,table)
        win+=1. if a>b else .5 if a==b else 0.
    return win/trials

@njit
def particles(h,b,n,runs,seed,table,pf):
    state=np.uint64(seed);known=np.uint64(0)
    for c in h:known|=np.uint64(1)<<np.uint64(c)
    for c in b:known|=np.uint64(1)<<np.uint64(c)
    strengths=np.zeros((n,4));wins=np.zeros(n);potential=np.zeros(n)
    other=np.empty(5,np.int32);future=np.empty(5,np.int32)
    for i in range(len(b)):future[i]=b[i]
    for p in range(n):
        used=known
        for i in range(5):
            while True:
                state,c=draw(state);bit=np.uint64(1)<<np.uint64(c)
                if not used&bit:break
            used|=bit;other[i]=c
        strengths[p,0]=pf[hand_id(other)]
        for st in range(1,4):
            if st+2<=len(b):strengths[p,st]=score(other,b[:st+2],table)
        for t in range(runs):
            mask=used
            for i in range(len(b),5):
                while True:
                    state,c=draw(state);bit=np.uint64(1)<<np.uint64(c)
                    if not mask&bit:break
                mask|=bit;future[i]=c
            a=score(h,future,table);v=score(other,future,table)
            wins[p]+=1. if a>v else .5 if a==v else 0.
        wins[p]/=runs
    return strengths,wins

_data=Path(__file__).resolve().parent/'data/opening_equity.npy'
if _data.exists():
    _OPEN=np.load(_data,allow_pickle=False)
elif os.environ.get('JISH5_TRAIN')=='1':
    _OPEN=np.full(376992,.5,np.float32)
else:raise FileNotFoundError('Include the entire jish_5 folder: data/opening_equity.npy is required')
if _OPEN.shape!=(376992,) or _OPEN.dtype!=np.float32 or not np.isfinite(_OPEN).all():raise ValueError('Invalid opening equity table')
_OPEN_SORT=np.sort(_OPEN)
particles(np.array([0,5,10,15,20],np.int32),np.array([24,29,34],np.int32),1,1,np.uint64(9),_LOOKUP,_OPEN)
equity_trials(np.array([0,5,10,15,20],np.int32),1,np.uint64(9),_LOOKUP)

# Rows: disciplined, balanced, loose/aggressive, indiscriminate, passive/station.
# Columns: bluff floor, value threshold, call width, raise aggression, check traps.
_PROFILES=np.array([[.025,.72,.00,.42,.12],[.10,.64,-.04,.65,.16],[.20,.56,-.11,.82,.10],[.86,.12,-.45,1.0,.01],[.025,.75,-.27,.12,.08]])
_SETTINGS={'value_margin': 0.045, 'future_tax': 0.18, 'induce': 0.3, 'range_power': 0.95}


def new_half(config: AgentConfig,memory:dict)->None:
    memory.clear()
    memory.update(config=config,prior=np.array([.20,.32,.18,.08,.22]),rng=random.Random(590172),
                  hand=-1,cache=None,seen=0,observations=[],last_obs=None,last_action=None,
                  compute_seconds=0.,decisions=0,hands_played=0,net=0,failures=0,
                  opportunity=np.ones((2,3))*4)


def _events(obs):
    # Reconstruct pot and outstanding bets solely from public action history.
    bets=[1 if obs.is_button else 2,2 if obs.is_button else 1]
    # Blinds may be customized by the judge; use observation's big blind.
    bets=[obs.big_blind//2 if obs.is_button else obs.big_blind,obs.big_blind if obs.is_button else obs.big_blind//2]
    pot=sum(bets);street=0;events=[]
    for e in obs.action_history:
        st=int(e.street)
        if st!=street:bets=[0,0];street=st
        seat=0 if e.is_me else 1;owed=max(0,bets[1-seat]-bets[seat])
        if not e.is_me:events.append((st,int(e.action),owed/max(1,pot+owed),owed>0,pot))
        pot+=e.amount;bets[seat]=e.street_total
    return events


def _probability(q,st,action,price,facing,profile):
    bluff,threshold,width,aggression,trap=profile
    # Preflop percentile remains wider than postflop made-hand percentile.
    threshold-=.12 if st==0 else 0.
    value=1/(1+np.exp(np.clip(-(q-threshold)*14,-30,30)))
    semi=(.08 if st in (1,2) else 0.)*4*q*(1-q)
    raised=np.clip(bluff+(1-bluff)*aggression*value+semi,.005,.98)
    if facing:
        boundary=np.clip(.16+1.25*price+width+(0.12 if st==0 else 0),.02,.85)
        cont=1/(1+np.exp(np.clip(-(q-boundary)*13,-30,30)))
        raised*=cont*(.55 if st==0 else .72)
        if action==0:return np.maximum(.003,1-cont)
        if action==1:return np.maximum(.003,cont-raised)
        return np.maximum(.003,raised)
    raised*=1-trap*np.maximum(0,(q-.75)/.25)
    return np.maximum(.003,1-raised if action==1 else raised)


def _analyse(obs,m):
    key=(obs.hand_index,tuple(obs.board))
    cached=m['cache']
    if cached is not None and cached['key']==key:return cached
    st=int(obs.street);n=768 if st==3 else 512;runs=1 if st==3 else 4
    elapsed=m['compute_seconds']/max(1,m['hands_played']+1)
    allowance=m['config'].time_bank_seconds/max(1,m['config'].num_hands)
    if elapsed>allowance*.64:n//=2
    h=np.array(obs.hole_cards,np.int32);b=np.array(obs.board,np.int32)
    if st==0:
        # A stratified sample of unknown opening holdings, conditioned on blockers.
        raw,out=particles(h,b,256,1,np.uint64(m['rng'].getrandbits(63)+1),_LOOKUP,_OPEN)
        mine=float(_OPEN[hand_id(h)])
        out=np.clip(.5+mine-raw[:,0],.02,.98)
    else:raw,out=particles(h,b,n,runs,np.uint64(m['rng'].getrandbits(63)+1),_LOOKUP,_OPEN)
    q=np.empty_like(raw)
    q[:,0]=np.searchsorted(_OPEN_SORT,raw[:,0],side='right')/len(_OPEN_SORT)
    hero=[]
    for s in range(1,st+1):
        a=np.sort(raw[:,s]);q[:,s]=(np.searchsorted(a,raw[:,s],side='left')+np.searchsorted(a,raw[:,s],side='right'))/(2*len(a))
        own=score(h,b[:s+2],_LOOKUP)
        hero.append(float((np.searchsorted(a,own,side='left')+np.searchsorted(a,own,side='right'))/(2*len(a))))
    result=dict(key=key,q=q,out=out,hero=hero,raw=raw)
    m['cache']=result
    return result


def _posterior(obs,m,sim):
    q=sim['q'];joint=np.ones((5,len(q)))*m['prior'][:,None]/len(q)
    for st,act,price,facing,_ in _events(obs):
        for k,p in enumerate(_PROFILES):joint[k]*=_probability(q[:,st],st,act,price,facing,p)**_SETTINGS['range_power']
        joint/=max(float(joint.sum()),1e-100)
    return joint/joint.sum()


def _tree(obs,m,sim,joint):
    st=int(obs.street);out=sim['out'];q=sim['q'][:,st]
    cost=min(obs.to_call,obs.my_stack);pot=obs.pot
    equity=float(np.sum(joint*out[None,:]));spr=max(0,min(obs.my_stack-cost,obs.opp_stack))/max(1,pot+cost)
    remaining=(3-st)/3
    # Paying future bets hurts marginal out-of-position holdings. Strong hands
    # retain implied value; no future charge remains on the river/all-in.
    tax=remaining*min(1,spr)*_SETTINGS['future_tax']*(1.15 if not obs.is_button else .65)
    realized=np.clip(equity-tax*(1-equity),0,1)
    call_ev=realized*(pot+cost)-cost
    if cost and call_ev<0:best,best_ev=Action.FOLD,0.
    else:best,best_ev=Action.CHECK_CALL,call_ev
    # Check branch can induce bets from bluff-heavy profiles. Its value is
    # evaluated separately from an immediate bet, rather than always checking
    # a fixed fraction of strong hands.
    if not cost and not obs.is_button and st>0:
        induced=0.
        for k,p in enumerate(_PROFILES):
            bet=_probability(q,st,2,.25,False,p)
            induced+=float(np.sum(joint[k]*bet*(2*out-1)))
        best_ev+=max(0,induced)*min(pot*.5,obs.opp_stack)*_SETTINGS['induce']
    baseline=best_ev
    for action in (Action.RAISE_HALF,Action.RAISE_POT):
        if action not in obs.legal_actions:continue
        investment=obs.raise_to[action]-obs.my_bet
        reply=min(obs.opp_stack,max(0,obs.raise_to[action]-obs.opp_bet))
        price=reply/max(1,pot+investment+reply)
        ev=0.;reraise_call=0.;reraise_fold=0.
        for k,p in enumerate(_PROFILES):
            fold=_probability(q,st,0,price,True,p)
            if cost:fold*=.42 # a bettor's range is less likely to fold to a raise
            # Range-weighted outcomes include hero blockers because sampled
            # holdings never contain hero's cards.
            cont=1-fold
            reraises=_probability(q,st,2,price,True,p)*cont
            if obs.raises_this_street>=m['config'].raise_cap-1 or min(obs.my_stack-investment,obs.opp_stack-reply)<=0:reraises*=0
            # Explicit opponent re-raise branch: additional legal pot-sized
            # exposure and our best fold/call response, capped by stacks.
            extra=max(0,min(obs.my_stack-investment,obs.opp_stack-reply,pot+investment+reply))
            val_call=out*(pot+investment+reply)-investment
            val_raise=out*(pot+investment+reply+2*extra)-investment-extra
            # Future realization penalty applies only while money remains.
            val_call-=remaining*min(1,spr)*investment*_SETTINGS['future_tax']*np.maximum(0,.65-out)
            ev+=float(np.sum(joint[k]*(fold*pot+(cont-reraises)*val_call)))
            reraise_call+=float(np.sum(joint[k]*reraises*val_raise))
            reraise_fold+=float(np.sum(joint[k]*reraises*(-investment)))
        # Our response to a re-raise is one decision over the entire inferred
        # range, never a separate decision using each hidden sampled hand.
        ev+=max(reraise_call,reraise_fold)
        margin=max(.20,pot*_SETTINGS['value_margin'])
        if ev>baseline+margin and ev>best_ev:best,best_ev=action,ev
    return best


def choose_action(obs:Observation,memory:dict)->Action:
    start=time.perf_counter()
    if memory['hand']!=obs.hand_index:memory.update(hand=obs.hand_index,cache=None)
    # Observe generic action frequencies for diagnostics; policy inference uses
    # complete public histories and is updated once at the end of a hand.
    sim=_analyse(obs,memory);joint=_posterior(obs,memory,sim)
    action=_tree(obs,memory,sim,joint)
    memory.update(last_obs=obs,last_action=action,last_joint=joint)
    memory['decisions']+=1;memory['compute_seconds']+=time.perf_counter()-start
    if action not in obs.legal_actions:raise ValueError('Strategy returned an illegal action')
    return action


def on_hand_end(result:HandResult,memory:dict)->None:
    # A conservative, decaying mixture update prevents one unusual hand from
    # classifying an opponent permanently. Never save information between halves.
    obs=memory.get('last_obs');joint=memory.get('last_joint')
    if obs is not None and obs.hand_index==result.hand_index and joint is not None:
        # The final response to our last bet is not in the preceding /act
        # observation. The terminal result still identifies a fold or call.
        # Include it so tight opponents can be distinguished from stations.
        if memory['last_action'] in (Action.RAISE_HALF,Action.RAISE_POT):
            target=obs.raise_to[memory['last_action']]
            reply=min(obs.opp_stack,max(0,target-obs.opp_bet))
            investment=target-obs.my_bet
            price=reply/max(1,obs.pot+investment+reply)
            response=0 if not result.went_to_showdown and result.winner=='me' else 1
            q=memory['cache']['q'][:,int(obs.street)]
            joint=joint.copy()
            for k,profile in enumerate(_PROFILES):
                joint[k]*=_probability(q,int(obs.street),response,price,True,profile)**_SETTINGS['range_power']
        p=joint.sum(axis=1);p=np.maximum(p,1e-6);p/=p.sum()
        p=np.maximum(p,.015);p/=p.sum()
        memory['prior']=.86*memory['prior']+.14*p
        memory['prior']=.97*memory['prior']+.03*np.array([.20,.32,.18,.08,.22])
    memory['hands_played']+=1;memory['net']+=result.my_net
    memory['cache']=None


# ===== END OF YOUR CODE =====


# ===== SERVER PLUMBING (you normally don't need to edit below) =====
# The judge calls these routes:
#   GET  /           -> who you are (also used as the health check)
#   POST /new-half   -> start a fresh half: memory is wiped
#   POST /act        -> the judge sends any finished hands plus an Observation;
#                       on_hand_end() runs for each hand, then you answer an action
#   POST /hand-end   -> the judge sends the last finished hands of a half
#
# Why "async def"? The routes run on one thread and call your functions
# directly, so your functions never run twice at once. Your own functions
# stay normal "def" (don't make them async).
#
# Keep your per-half state in `memory`. In the tournament every half runs in
# a fresh server process, so everything starts over. When you test locally,
# though, one process can play both halves and only `memory` is wiped, NOT
# other global variables. Using `memory` makes your bot behave the same way
# in both places.

app = FastAPI()
MEMORY: dict = {}                                   # your memory for this half
STATUS = {"started": False}                         # has /new-half been called?
TOKEN = os.environ.get("AGENT_TOKEN") or None       # set by the tournament


async def _read_request(request: Request, path: str) -> tuple[dict, JSONResponse | None]:
    """Check the token (and that the half has started) BEFORE reading the body.

    Checking first means a request without the right token costs your bot
    almost nothing, so nobody else can slow it down by sending junk.
    Returns (body, None) when the request is fine, or ({}, error response).
    """
    if TOKEN and request.headers.get("x-agent-token") != TOKEN:
        return {}, JSONResponse({"error": "bad or missing X-Agent-Token"}, status_code=401)
    if not STATUS["started"] and path != "/new-half":
        return {}, JSONResponse({"error": "call /new-half first"}, status_code=409)
    try:
        body = await request.json()
    except ValueError:
        body = None
    if not isinstance(body, dict):
        return {}, JSONResponse({"error": "the request body must be a JSON object"}, status_code=400)
    return body, None


def _error_info(exc: Exception) -> dict:
    """Describe an exception from your code (call this inside `except`)."""
    return {"error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()}


def _crash(exc: Exception, hand_end_errors: list | None = None) -> JSONResponse:
    """Report an exception from your code to the judge (with traceback)."""
    return JSONResponse({**_error_info(exc), "hand_end_errors": hand_end_errors or []},
                        status_code=500)


def _deliver_results(raw_results) -> list:
    """Call on_hand_end() for each finished hand the judge sent.
    Returns a list of error reports (one per hand that crashed)."""
    errors = []
    for raw in raw_results or []:
        try:
            on_hand_end(HandResult.from_dict(raw), MEMORY)
        except Exception as exc:
            errors.append(_error_info(exc))
    return errors


@app.get("/")
async def info():
    """Health check: tells the judge who this bot is."""
    return {"participant": PARTICIPANT, "agent_name": AGENT_NAME}


@app.post("/new-half")
async def route_new_half(request: Request):
    """Wipe memory and call your new_half(). The body is {"config": {...}}."""
    body, refused = await _read_request(request, "/new-half")
    if refused:
        return refused
    MEMORY.clear()
    STATUS["started"] = True
    try:
        new_half(AgentConfig.from_dict(body.get("config", {})), MEMORY)
    except Exception as exc:
        return _crash(exc)
    return {"ok": True}


@app.post("/act")
async def route_act(request: Request):
    """Deliver finished hands, then turn the JSON into an Observation, call
    choose_action(), and send the answer back."""
    body, refused = await _read_request(request, "/act")
    if refused:
        return refused
    hand_end_errors = _deliver_results(body.get("hand_results"))
    try:
        obs = Observation.from_dict(body["observation"])
        action = choose_action(obs, MEMORY)
    except Exception as exc:
        return _crash(exc, hand_end_errors)
    # Send the action's name; anything strange is passed on for the judge to reject.
    if isinstance(action, Action):
        answer = action.name
    elif action is None or isinstance(action, (str, int, float, bool)):
        answer = action
    else:
        answer = repr(action)
    return {"action": answer, "hand_end_errors": hand_end_errors}


@app.post("/hand-end")
async def route_hand_end(request: Request):
    """Call on_hand_end() for the last finished hands of a half."""
    body, refused = await _read_request(request, "/hand-end")
    if refused:
        return refused
    return {"ok": True, "hand_end_errors": _deliver_results(body.get("results"))}


if __name__ == "__main__":
    # The tournament sets PORT as an environment variable, so each bot is compliant to our evaluation platform
    # Locally it defaults to 5008 for your own testing convenience
    port = int(os.environ.get("PORT", "5008"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info", access_log=False)
