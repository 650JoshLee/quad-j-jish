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

TODO:
    1. Assign your agent a unique PARTICIPANT and AGENT_NAME below.
    2. Implement the three functions between "YOUR CODE HERE" and "END OF YOUR CODE".

Everything under "SERVER PLUMBING" talks to the judge. You normally never
need to change it, and if you break it the judge can't talk to your bot.
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

# rename as your team/bot's name
PARTICIPANT = "quad-j"
AGENT_NAME = "jish_6"


# ===== YOUR CODE HERE =====

# Strategy sources: RESEARCH_SPEC.txt and the official participant bundle.
# Hold'em charts are replaced by fresh estimates under the actual PLO rules.
import math
import random
import time
from itertools import combinations, permutations
from pathlib import Path
import numpy as np
from numba import njit
from evaluator import get_table

# Exact numerical acceleration of the official evaluator: any legal five-card
# score can be addressed by its chosen hole pair and chosen board triple.
_PAIR=np.full((36,36),-1,np.int32)
_TRIPLE=np.full((36,36,36),-1,np.int32)
for i,(a,b) in enumerate(combinations(range(36),2)):
    _PAIR[a,b]=_PAIR[b,a]=i
for i,t in enumerate(combinations(range(36),3)):
    for a,b,c in permutations(t):_TRIPLE[a,b,c]=i
_FIVES=np.array(list(combinations(range(36),5)),dtype=np.int16)
_five_masks=np.left_shift(np.uint64(1),_FIVES.astype(np.uint64)).sum(axis=1)
_ref=get_table()
_ref_values=np.fromiter((_ref[int(m)] for m in _five_masks),dtype=np.int32,count=len(_FIVES))
_GRID=np.zeros((630,7140),np.int32)
for x,y in combinations(range(5),2):
    a,b,c=[i for i in range(5) if i not in (x,y)]
    _GRID[_PAIR[_FIVES[:,x],_FIVES[:,y]],_TRIPLE[_FIVES[:,a],_FIVES[:,b],_FIVES[:,c]]]=_ref_values
_sort=np.argsort(_five_masks)
_MASKS=_five_masks[_sort]
_HANDS=_FIVES[_sort].astype(np.int32)
for _constant in (_PAIR,_TRIPLE,_GRID,_MASKS,_HANDS):_constant.flags.writeable=False

@njit
def _key(cards):
    key=np.uint64(0)
    for c in cards:key|=np.uint64(1)<<np.uint64(c)
    return key

@njit
def _value(hand,board,grid):
    best=0
    for a in range(4):
        for b in range(a+1,5):
            pair=_PAIR[hand[a],hand[b]]
            for i in range(len(board)-2):
                for j in range(i+1,len(board)-1):
                    for k in range(j+1,len(board)):
                        v=grid[pair,_TRIPLE[board[i],board[j],board[k]]]
                        if v>best:best=v
    return best

@njit
def _potential(hand,board):
    # This estimates draws from known cards, never from an unrevealed deal.
    # A flush draw needs TWO same-suit private cards in Omaha.
    result=0.
    for suit in range(4):
        public=0;private=0;top=-1
        for c in board:
            if c%4==suit:public+=1
        for c in hand:
            if c%4==suit:private+=1;top=max(top,c//4)
        if public==2 and private>=2:result=max(result,.25+.65*top/8)
    ranks=0
    for c in hand:ranks|=1<<(c//4)
    # Connected private holdings are potential, not automatically made straights.
    for start in range(5):
        count=0
        for r in range(start,start+5):count+=int(bool(ranks&(1<<r)))
        if count>=3:result=max(result,.20)
    return result

@njit
def _trials(hand,board,count,repetitions,seed,grid,opening):
    np.random.seed(seed)
    used_initial=_key(hand)|_key(board)
    holes=np.empty((count,5),np.int32)
    # Columns: preflop equity and made scores on each revealed street.
    states=np.zeros((count,4));draws=np.zeros((count,4));wins=np.zeros(count)
    final=np.empty(5,np.int32)
    for k in range(len(board)):final[k]=board[k]
    for row in range(count):
        used=used_initial
        for j in range(5):
            while True:
                card=np.random.randint(36);bit=np.uint64(1)<<np.uint64(card)
                if not used&bit:break
            holes[row,j]=card;used|=bit
        other=holes[row]
        states[row,0]=opening[np.searchsorted(_MASKS,_key(other))]
        for st in range(1,4):
            if st+2<=len(board):
                states[row,st]=_value(other,board[:st+2],grid)
                draws[row,st]=_potential(other,board[:st+2]) if st<3 else 0.
        for repeat in range(repetitions):
            occupied=used
            for j in range(len(board),5):
                while True:
                    card=np.random.randint(36);bit=np.uint64(1)<<np.uint64(card)
                    if not occupied&bit:break
                final[j]=card;occupied|=bit
            a=_value(hand,final,grid);b=_value(other,final,grid)
            wins[row]+=(1.0 if a>b else 0.5 if a==b else 0.0)
        wins[row]/=repetitions
    return holes,states,draws,wins

@njit
def _opening_trials(hand,repeats,seed,grid):
    np.random.seed(seed);occupied=_key(hand)
    other=np.empty(5,np.int32);board=np.empty(5,np.int32);total=0.
    for n in range(repeats):
        used=occupied
        for j in range(10):
            while True:
                c=np.random.randint(36);bit=np.uint64(1)<<np.uint64(c)
                if not used&bit:break
            used|=bit
            if j<5:other[j]=c
            else:board[j-5]=c
        a=_value(hand,board,grid);b=_value(other,board,grid)
        total+=(1.0 if a>b else 0.5 if a==b else 0.0)
    return total/repeats

_opening_path=Path(__file__).resolve().parent/'data/research_opening.npy'
if _opening_path.exists():_OPENING=np.load(_opening_path,allow_pickle=False)
elif os.environ.get('RESEARCH_TRAIN')=='1':_OPENING=np.full(len(_MASKS),.5,np.float32)
else:raise FileNotFoundError('Keep data/research_opening.npy with agent.py; submit the whole jish_6 folder')
if _OPENING.shape!=(376992,) or _OPENING.dtype!=np.float32 or not np.isfinite(_OPENING).all():raise ValueError('Invalid research opening data')
_OPENING_ORDER=np.sort(_OPENING)
_trials(np.array([0,5,10,15,20],np.int32),np.array([24,29,34],np.int32),1,1,71,_GRID,_OPENING)
_opening_trials(np.array([0,5,10,15,20],np.int32),1,71,_GRID)


def new_half(config:AgentConfig,memory:dict)->None:
    memory.clear()
    memory.update(config=config,rng=random.Random(610071),statistics=np.zeros((4,2,4)),
                  hand_id=-1,observed=0,simulation=None,last=None,last_move=None,
                  elapsed=0.,decisions=0,hands=0,net=0)


def _history(obs,cfg):
    # Public replay supplies the price and distinguishes checking from calling.
    totals=[cfg.small_blind,cfg.big_blind] if obs.is_button else [cfg.big_blind,cfg.small_blind]
    pot=sum(totals);street=0;voluntary=[0,0,0,0]
    result=[]
    for e in obs.action_history:
        if int(e.street)!=street:street=int(e.street);totals=[0,0]
        seat=0 if e.is_me else 1
        price=max(0,totals[1-seat]-totals[seat])
        facing=int(price>0 and (street>0 or voluntary[0]>0))
        if e.action==Action.FOLD:category=3
        elif e.action in (Action.RAISE_HALF,Action.RAISE_POT):category=2
        else:category=int(price>0)
        result.append((e.is_me,street,facing,category,price/max(1,pot+price)))
        if category==2:voluntary[street]+=1
        totals[seat]=e.street_total;pot+=e.amount
    return result


def _rates(memory,street,facing):
    # Beta-style shrinkage implements the research's evidence requirement.
    pool=memory['statistics'][street,facing]
    if street:pool=pool+.30*memory['statistics'][1:,facing].sum(axis=0)
    prior=np.array([0.,15.,6.,9.]) if facing else np.array([16.,0.,14.,0.])
    probabilities=(pool+prior)/(pool.sum()+30)
    confidence=min(.65,max(0.,(pool.sum()-60)/180))
    return probabilities,confidence


def _texture(board):
    suits=[sum(c%4==s for c in board) for s in range(4)]
    ranks=[c//4 for c in board]
    paired=len(set(ranks))<len(ranks)
    connected=any(sum(start<=r<=start+4 for r in set(ranks))>=3 for start in range(5))
    wet=max(suits)>=2 or connected
    return paired,wet,max(suits)>=3


def _percentiles(values):
    ordered=np.sort(values)
    return (np.searchsorted(ordered,values,'left')+np.searchsorted(ordered,values,'right'))/(2*len(values))


def _particles(obs,memory):
    signature=(obs.hand_index,tuple(obs.board))
    if memory['simulation'] is not None and memory['simulation']['signature']==signature:return memory['simulation']
    st=int(obs.street);h=np.array(obs.hole_cards,np.int32);b=np.array(obs.board,np.int32)
    budget=memory['config'].time_bank_seconds*.45/max(1,memory['config'].num_hands)
    average=memory['elapsed']/max(1,memory['hands']+1)
    factor=min(1.,budget/max(budget,average))
    n=max(128,int((768 if st==3 else 512)*factor));repeats=1 if st==3 else 3
    if not st:n=192;repeats=2
    holes,states,draws,wins=_trials(h,b,n,repeats,memory['rng'].randrange(1,2147483647),_GRID,_OPENING)
    quantiles=np.zeros_like(states)
    quantiles[:,0]=np.searchsorted(_OPENING_ORDER,states[:,0])/len(_OPENING_ORDER)
    for k in range(1,st+1):quantiles[:,k]=_percentiles(states[:,k])
    if not st:
        own=float(_OPENING[np.searchsorted(_MASKS,_key(h))])
        # Shrink noisy direct preflop outcomes to the independently simulated
        # opening estimates, still conditioned on the sampled opponent range.
        wins=.35*wins+.65*np.clip(.5+own-states[:,0],0.,1.)
        own_rank=float(np.searchsorted(_OPENING_ORDER,own)/len(_OPENING_ORDER))
    else:
        current=_value(h,b,_GRID);own_rank=float(np.mean(states[:,st]<current)+.5*np.mean(states[:,st]==current))
    data=dict(signature=signature,holes=holes,q=quantiles,draws=draws,wins=wins,rank=own_rank)
    memory['simulation']=data
    return data


def _range(obs,memory,data,events):
    weights=np.ones(len(data['wins']));raised=[0,0,0,0]
    for is_me,st,facing,category,price in events:
        previous_raises=raised[st]
        if category==2:raised[st]+=1
        if is_me:continue
        q=data['q'][:,st];draw=data['draws'][:,st]
        rates,confidence=_rates(memory,st,facing)
        if category==2:
            # Polarized value plus a bounded bluff/draw component, with wider
            # raises against opponents whose observed aggression is frequent.
            boundary=(.16 if previous_raises==0 else .82 if previous_raises==1 else .91) if st==0 else .66
            if st==0 and previous_raises>0:boundary=(1-confidence)*boundary+confidence*(1-rates[2])
            boundary-=.20*confidence*max(0.,rates[2]-.35)
            passivity=max(0.,(.30-rates[2])/.30)
            if st>0:boundary+=.18*confidence*passivity
            air=.12*(1-.75*confidence*passivity)
            likelihood=np.where(q>=boundary,.85,np.where(draw>.55,.42,air))
            likelihood+=confidence*min(.30,max(0.,rates[2]-.35))
        elif category==1:
            likelihood=.30+.65*np.sqrt(q)+.15*draw
        elif category==0:
            # Strong hands remain in checking ranges; a check never proves a cap.
            likelihood=np.where(q>.90,.35,np.where(q<.60,.90,.65))
            likelihood=(1-confidence)*likelihood+confidence*max(.25,rates[0])
        else:continue
        weights*=np.maximum(.05,likelihood)**.65
    return weights/weights.sum()


def _blocker(hand,board):
    # One ace can block another player's nut flush, but cannot itself make an
    # Omaha flush. Drawing and made-hand evaluation still enforce exactly 2+3.
    score=0.
    if not board:return min(1.,.35*sum(c//4==8 for c in hand)+.15*sum(c//4==7 for c in hand))
    for suit in range(4):
        if sum(c%4==suit for c in board)>=2:
            if 32+suit in hand:score+=.6
            elif 28+suit in hand:score+=.25
    return min(1.,score)


def _policy(obs,memory):
    if memory['hand_id']!=obs.hand_index:memory.update(hand_id=obs.hand_index,observed=0,simulation=None)
    events=_history(obs,memory['config'])
    for is_me,st,facing,category,price in events[memory['observed']:]:
        if not is_me:memory['statistics'][st,facing,category]+=1
    memory['observed']=len(events)
    data=_particles(obs,memory);weights=_range(obs,memory,data,events)
    st=int(obs.street);position=obs.is_button;cost=min(obs.my_stack,obs.to_call)
    pot=max(1,obs.pot);odds=cost/(pot+cost);equity=float(weights@data['wins'])
    stack=max(0,min(obs.my_stack-cost,obs.opp_stack));spr=stack/(pot+cost)
    h=obs.hole_cards;blocker=_blocker(h,obs.board)
    facing,confidence=_rates(memory,st,1);free_rates,free_confidence=_rates(memory,st,0)
    aggressive=confidence*max(0.,(facing[2]-.30)/.50)
    station=confidence*max(0.,(.20-facing[3])/.20)
    folder=confidence*max(0.,(facing[3]-.40)/.35)
    draws=_potential(np.array(h,np.int32),np.array(obs.board,np.int32)) if st in (1,2) else 0.
    q=data['rank'];rng=memory['rng'];available=[a for a in obs.legal_actions if a in (Action.RAISE_HALF,Action.RAISE_POT)]
    if st==0:
        own=float(_OPENING[np.searchsorted(_MASKS,_key(np.array(h,np.int32)))])
        raises=sum(not me and category==2 for me,_,_,category,_ in events)
        # Wide positional opening is retained as a principle, while actual PLO
        # equity and 40BB commitment replace the research's Hold'em hand charts.
        adjusted=equity-(.025 if raises else 0.)*(1-aggressive)
        if raises>=2:adjusted-=.025*(1-aggressive)
        if available and obs.raises_this_street==0:
            opening=.84 if position else .24
            opening=min(.97,opening+.12*folder)
            if q>1-opening and own>.38:
                return Action.RAISE_HALF if rng.random()<(.75 if position else .35) else Action.RAISE_POT
        if available and q>.90 and adjusted>.51:return Action.RAISE_POT
        if available and q<.25 and blocker>.4 and rng.random()<.06*(1-station):return Action.RAISE_HALF
        if not cost:return Action.CHECK_CALL
        premium=(.065 if not position else .035)*min(1.,spr)*(1-aggressive)
        if aggressive>.35 and raises>=2:premium=max(premium,.49-odds)
        return Action.CHECK_CALL if adjusted>=odds+premium else Action.FOLD
    paired,wet,monotone=_texture(obs.board)
    # A low SPR never makes a single pair automatically committed in PLO.
    reserve=(.018 if position else .035)*min(1.,spr)*(3-st)/2
    call_value=equity*(pot+cost)-cost-reserve*(pot+cost)*(1-equity)
    values={Action.CHECK_CALL:call_value}
    if cost:values[Action.FOLD]=0.
    # Protected checking ranges and occasional traps on safe textures.
    trap=(not wet and q>.92 and rng.random()<.12+.18*aggressive and not cost and station<.15)
    if trap:return Action.CHECK_CALL
    for action in available:
        payment=obs.raise_to[action]-obs.my_bet
        reply=min(obs.opp_stack,max(0,obs.raise_to[action]-obs.opp_bet))
        fraction=reply/max(1,pot+payment+reply)
        expected_fold=.27+.65*(fraction-.25)+.25*folder-.40*station
        if cost:expected_fold*=.60
        expected_fold=float(np.clip(expected_fold,.025,.65))
        # Select a continuing range by a soft, weighted lower-tail cut. The
        # sizes target different tails; strong draws resist folding early.
        quality=data['q'][:,st] if st==3 else .75*data['q'][:,st]+.25*data['draws'][:,st]
        order=np.argsort(quality);cumulative=np.cumsum(weights[order]);fold=np.zeros(len(weights))
        fold[order]=np.clip((expected_fold-cumulative+.075)/.15,0.,1.)
        continuation=weights*(1-fold);continued=float(continuation.sum())
        eq_called=float(continuation@data['wins']/max(continued,1e-9))
        bet_value=(1-continued)*pot+continued*(eq_called*(pot+payment+reply)-payment)
        # Future pressure and re-raises make medium-strength stack-offs costly.
        if st<3 and stack>0:
            bet_value-=continued*payment*max(0.,.58-eq_called)*min(1.,spr)*.65
        # Nut advantage favors the larger legal size; protection prefers half.
        if action==Action.RAISE_POT and q<.80 and not draws>.55:bet_value-=pot*.02
        if action==Action.RAISE_HALF and not wet and q>.55:bet_value+=pot*.008
        # The research's river bluff fraction is a mixing ceiling, not evidence
        # that an otherwise unprofitable bluff should be fired automatically.
        if equity<.35:
            bluff_share=fraction
            eligibility=(.25+.75*blocker+.5*draws)*(1-station)
            if rng.random()>bluff_share*min(1.,eligibility):continue
        values[action]=bet_value-pot*.015
    best=max(values,key=values.get);best_value=values[best]
    # Mix only nearly equivalent actions; never sacrifice a clearly positive
    # call just to mechanically satisfy MDF against a value-only range.
    near=[a for a,v in values.items() if v>=best_value-max(.12,pot*.012)]
    if len(near)>1:best=rng.choice(near)
    return best


def choose_action(obs:Observation,memory:dict)->Action:
    started=time.perf_counter()
    action=_policy(obs,memory)
    memory['last']=obs;memory['last_move']=action;memory['decisions']+=1
    memory['elapsed']+=time.perf_counter()-started
    if action not in obs.legal_actions:raise ValueError('Nonlegal action selected')
    return action


def on_hand_end(result:HandResult,memory:dict)->None:
    obs=memory.get('last');action=memory.get('last_move')
    # Final responses are visible in terminal outcomes even though they are
    # absent from the preceding observation's action history.
    if obs is not None and obs.hand_index==result.hand_index and action in (Action.RAISE_HALF,Action.RAISE_POT):
        if result.winner=='me' and not result.went_to_showdown:memory['statistics'][int(obs.street),1,3]+=1
        elif result.went_to_showdown:memory['statistics'][int(obs.street),1,1]+=1
    memory['hands']+=1;memory['net']+=result.my_net
    memory['simulation']=None


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
