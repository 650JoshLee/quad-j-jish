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
AGENT_NAME = "jish_10"


# ===== YOUR CODE HERE =====

"""Independent sampled-equity and one-street CFR+ abstraction.

Inspired by Eric Jackson's published CFR research, not Slumbot's Hold'em policy.
No earlier jish policy, helper implementation, or trained data is used here.
"""
import itertools
import math
import time
import numpy as np
from numba import njit
from evaluator import score_five

_TYPES = 8
_ITERATIONS = 64
_RANGE_SCALE = 1.0
_STREET_SPREAD = (0.22, 0.78, 0.9, 1.0)


def _make_scores():
    result = np.zeros((2, 9**5), dtype=np.int32)
    for ranks in itertools.combinations_with_replacement(range(9), 5):
        if max(ranks.count(r) for r in ranks) > 4:
            continue
        used = {}
        cards = []
        for r in ranks:
            suit = used.get(r, 0); used[r] = suit+1
            cards.append(4*r+suit)
        plain = score_five(cards)
        # Distinct ranks can be either flush or nonflush.
        if len(set(ranks)) == 5:
            plain = score_five([4*r+(i%4) for i,r in enumerate(ranks)])
            flush = score_five([4*r for r in ranks])
        else:
            flush = plain
        for order in set(itertools.permutations(ranks)):
            key = sum(r*9**i for i,r in enumerate(order))
            result[0,key],result[1,key] = plain,flush
    return result


_FIVE = _make_scores()


@njit
def _omaha(hole, board, table):
    best = 0
    for a in range(4):
        for b in range(a+1,5):
            x,y = hole[a],hole[b]
            prefix = (x//4)+9*(y//4)
            for c in range(len(board)-2):
                for d in range(c+1,len(board)-1):
                    for e in range(d+1,len(board)):
                        u,v,w = board[c],board[d],board[e]
                        flush = int(x%4==y%4 and y%4==u%4 and u%4==v%4 and v%4==w%4)
                        key=prefix+81*(u//4)+729*(v//4)+6561*(w//4)
                        best=max(best,table[flush,key])
    return best


@njit
def _equity(hole, board, count, seed, table):
    # A local generator avoids shared random state across bot processes/halves.
    state=np.uint64(seed)|np.uint64(1)
    known=np.zeros(36,np.uint8)
    for c in hole:known[c]=1
    for c in board:known[c]=1
    deck=np.empty(36-len(hole)-len(board),np.int32);n=0
    for c in range(36):
        if not known[c]:deck[n]=c;n+=1
    other=np.empty(5,np.int32);full=np.empty(5,np.int32)
    for i in range(len(board)):full[i]=board[i]
    total=0.;squares=0.
    for sample in range(count):
        # Partial Fisher-Yates: every sample is a legal joint hand/runout.
        pool=deck.copy()
        for j in range(10-len(board)):
            state ^= state << np.uint64(13)
            state ^= state >> np.uint64(7)
            state ^= state << np.uint64(17)
            pick=j+int(state%np.uint64(n-j))
            pool[j],pool[pick]=pool[pick],pool[j]
            if j<5:other[j]=pool[j]
            else:full[len(board)+j-5]=pool[j]
        ours=_omaha(hole,full,table);theirs=_omaha(other,full,table)
        value=1. if ours>theirs else .5 if ours==theirs else 0.
        total+=value;squares+=value*value
    return total/count, max(0.,squares/count-(total/count)**2)


def _betting_tree(obs, cap=4):
    """Exact current-street legal bet transitions; future streets are abstracted."""
    actors=[];children=[];terminal=[];spent=[]
    original=(obs.my_stack,obs.opp_stack)
    other_acted=any(not h.is_me and h.street==obs.street for h in obs.action_history)
    def visit(stacks,bets,acted,who,raises,increment,kind=-1):
        idx=len(actors);actors.append(who if kind<0 else -1)
        children.append([-1]*4);terminal.append(kind)
        spent.append([original[0]-stacks[0],original[1]-stacks[1]])
        if kind>=0:return idx
        call=max(0,bets[1-who]-bets[who])
        legal=[1] if call==0 else [0,1]
        if raises<cap and stacks[who]>call and stacks[1-who]>0:legal += [2,3]
        pot=obs.pot+sum(original)-sum(stacks)
        for action in legal:
            if action==0:
                # terminal kind 1: player 0 wins; kind 2: player 1 wins.
                child=visit(stacks,bets,acted,who,raises,increment,2 if who==0 else 1)
            else:
                s=list(stacks);b=list(bets);a=list(acted);r=raises;inc=increment
                amount=min(call,s[who])
                if action>=2:
                    max_to=b[1-who]+pot+call
                    target=b[1-who]+((pot+call)//2 if action==2 else pot+call)
                    target=min(max(target,b[1-who]+max(inc,obs.big_blind)),max_to,b[who]+s[who])
                    amount=target-b[who];inc=target-b[1-who];r+=1;a[1-who]=False
                s[who]-=amount;b[who]+=amount;a[who]=True
                end=a[0] and a[1] and b[0]==b[1]
                child=visit(s,b,a,1-who,r,inc,0 if end else -1)
            children[idx][action]=child
        return idx
    visit(original,(obs.my_bet,obs.opp_bet),(False,other_acted),0,obs.raises_this_street,max(obs.big_blind,obs.min_raise_to-obs.opp_bet))
    return np.array(actors,np.int32),np.array(children,np.int32),np.array(terminal,np.int32),np.array(spent,np.float64)


def _payoffs(kinds,spent,pot,spread,types=_TYPES):
    order=np.arange(types)
    win=.5+spread*.5*np.sign(order[:,None]-order[None,:])
    payoff=np.zeros((len(kinds),types,types))
    for n,kind in enumerate(kinds):
        if kind<0:continue
        a,b=spent[n]
        if kind==0:payoff[n]=win*(pot+a+b)-a-pot/2
        elif kind==1:payoff[n]=pot/2+b
        else:payoff[n]=-pot/2-a
    return payoff


@njit
def _solve(actors,children,payoff,joint,iterations):
    """Full-tree regret matching+ with linearly weighted average strategies."""
    nodes=len(actors);types=len(joint)
    regret=np.zeros((nodes,types,4));average=np.zeros_like(regret)
    strategy=np.zeros_like(regret)
    reach=np.zeros((nodes,2,types));values=np.zeros_like(reach)
    action_values=np.zeros((types,4))
    for iteration in range(iterations):
        reach[:]=0.;reach[0,:,:]=1.
        for node in range(nodes):
            actor=actors[node]
            if actor<0:continue
            count=0
            for a in range(4):
                if children[node,a]>=0:count+=1
            for t in range(types):
                mass=0.
                for a in range(4):
                    if children[node,a]>=0:mass+=regret[node,t,a]
                for a in range(4):
                    child=children[node,a]
                    if child<0:continue
                    p=regret[node,t,a]/mass if mass>1e-20 else 1./count
                    strategy[node,t,a]=p
                    average[node,t,a]+=(iteration+1)*reach[node,actor,t]*p
                    reach[child,actor,t]=reach[node,actor,t]*p
                    reach[child,1-actor,t]=reach[node,1-actor,t]
        values[:]=0.
        for node in range(nodes-1,-1,-1):
            actor=actors[node]
            if actor<0:
                for x in range(types):
                    for y in range(types):
                        u=joint[x,y]*payoff[node,x,y]
                        values[node,0,x]+=reach[node,1,y]*u
                        values[node,1,y]-=reach[node,0,x]*u
            else:
                for t in range(types):
                    for a in range(4):
                        child=children[node,a]
                        if child<0:continue
                        action_values[t,a]=values[child,actor,t]
                        values[node,actor,t]+=strategy[node,t,a]*values[child,actor,t]
                        values[node,1-actor,t]+=values[child,1-actor,t]
                    for a in range(4):
                        if children[node,a]>=0:
                            regret[node,t,a]=max(0.,regret[node,t,a]+action_values[t,a]-values[node,actor,t])
    for n in range(nodes):
        for t in range(types):
            total=average[n,t].sum()
            if total>0:average[n,t]/=total
    return average


def _priors(obs,memory):
    levels=(np.arange(_TYPES)+.5)/_TYPES
    priors=np.ones((2,_TYPES))
    # Both ranges depend only on public actions; neither gets our actual hand.
    rates=memory['opponent_actions']
    aggression=(rates[2]+2)/(rates.sum()+6)
    for event in obs.action_history:
        actor=0 if event.is_me else 1
        age=.55**(int(obs.street)-int(event.street))
        if event.action in (Action.RAISE_HALF,Action.RAISE_POT):
            slope=(2.8 if actor==0 else 4.*max(0.,1.-aggression/.65))*age
            priors[actor]*=np.exp(_RANGE_SCALE*slope*(levels-.5))
        elif event.amount>0:
            priors[actor]*=.7+.6*levels
    priors+=.04
    priors/=priors.sum(axis=1)[:,None]
    return priors[0,:,None]*priors[1,None,:]


def new_half(config: AgentConfig,memory: dict) -> None:
    memory.clear()
    memory.update(config=config,rng=np.random.default_rng(100103),opponent_actions=np.zeros(3),
                  hand=-1,seen=0,estimate_key=None,estimate=None,compute_seconds=0.,
                  decisions=0,hands_played=0,fallback_count=0)


def choose_action(obs: Observation,memory: dict) -> Action:
    started=time.perf_counter()
    if memory['hand']!=obs.hand_index:memory.update(hand=obs.hand_index,seen=0)
    for event in obs.action_history[memory['seen']:]:
        if not event.is_me:
            index=0 if event.action==Action.FOLD else 1 if event.action==Action.CHECK_CALL else 2
            memory['opponent_actions'][index]+=1
    memory['seen']=len(obs.action_history)
    key=(obs.hand_index,obs.hole_cards,obs.board)
    if key!=memory['estimate_key']:
        count=768 if not obs.board else 256
        equity,variance=_equity(np.array(obs.hole_cards,np.int32),np.array(obs.board,np.int32),count,
                                np.uint64(memory['rng'].integers(1,2**62)),_FIVE)
        memory.update(estimate_key=key,estimate=equity)
    equity=memory['estimate'];street=int(obs.street)
    actors,children,kinds,spent=_betting_tree(obs,memory['config'].raise_cap)
    spread=_STREET_SPREAD[street]
    payoff=_payoffs(kinds,spent,obs.pot,spread)
    # Adapt only computational effort, not strategic parameters, to time use.
    target=memory['config'].time_bank_seconds*.55/max(1,memory['config'].num_hands)
    spent_per_hand=memory['compute_seconds']/max(1,obs.hand_index+1)
    iterations=max(16,int(_ITERATIONS*min(1.,target/max(target,spent_per_hand))))
    policy=_solve(actors,children,payoff,_priors(obs,memory),iterations)
    strength=min(1.-1e-10,max(0.,.5+(equity-.5)/spread))
    bucket=min(_TYPES-1,int(strength*_TYPES))
    probs=policy[0,bucket].copy()
    for action in Action:
        if action not in obs.legal_actions:probs[int(action)]=0.
    probs/=probs.sum()
    action=Action(int(memory['rng'].choice(4,p=probs)))
    memory['compute_seconds']+=time.perf_counter()-started
    memory['decisions']+=1
    return action


def on_hand_end(result: HandResult,memory: dict) -> None:
    memory['hands_played']+=1


# Warm compiled kernels during startup, never on the first charged decision.
_equity(np.array([0,5,10,15,20],np.int32),np.array([24,29,34],np.int32),2,np.uint64(17),_FIVE)
_solve(np.array([0,-1,-1],np.int32),np.array([[-1,1,2,-1],[-1]*4,[-1]*4],np.int32),
       np.zeros((3,_TYPES,_TYPES)),np.full((_TYPES,_TYPES),1./_TYPES**2),2)

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
