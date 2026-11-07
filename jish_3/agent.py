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

Team: quad-j. Bot: jish_3.
Strategy: refined preflop equity, complete conditional runouts,
exact river enumeration when the compute allowance permits, and
opponent-adapted betting. See BOT_NOTES.md.

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

# Tournament identity
PARTICIPANT = "quad-j"
AGENT_NAME = "jish_3"


# ===== YOUR CODE HERE =====

# The strategy and its numerical helpers live inside the editable section.
# Numba compiles these loops during startup; matches need no network or writes.
import math
import random
import time
from itertools import combinations, combinations_with_replacement
from pathlib import Path

import numpy as np
from numba import njit
from evaluator import _score_ranks

_RANK_POWER = np.array([5 ** (c >> 2) for c in range(36)], dtype=np.int32)
_SUIT_BIT = np.array([1 << (c & 3) for c in range(36)], dtype=np.int32)
_BINOM = np.zeros((36, 6), dtype=np.int32)
for _c in range(36):
    for _k in range(6):
        _BINOM[_c, _k] = math.comb(_c, _k) if _c >= _k else 0
_SCORE = np.zeros((2, 5 ** 9), dtype=np.int32)
for _ranks in combinations_with_replacement(range(9), 5):
    if max(_ranks.count(r) for r in _ranks) > 4:
        continue
    _key = sum(5 ** r for r in _ranks)
    _SCORE[0, _key] = _score_ranks(tuple(reversed(_ranks)), False)
    _SCORE[1, _key] = _score_ranks(tuple(reversed(_ranks)), True)


@njit
def _index(hole):
    ordered = np.sort(hole)
    idx = 0
    for i in range(5):
        idx += _BINOM[ordered[i], i + 1]
    return idx


@njit
def _pairs(hole):
    ranks = np.empty(10, dtype=np.int32)
    suits = np.empty(10, dtype=np.int32)
    n = 0
    for i in range(5):
        for j in range(i + 1, 5):
            ranks[n] = _RANK_POWER[hole[i]] + _RANK_POWER[hole[j]]
            suits[n] = _SUIT_BIT[hole[i]] & _SUIT_BIT[hole[j]]
            n += 1
    return ranks, suits


@njit
def _score_pairs(ranks, suits, board, length, table):
    best = 0
    for i in range(length - 2):
        for j in range(i + 1, length - 1):
            for k in range(j + 1, length):
                br = _RANK_POWER[board[i]] + _RANK_POWER[board[j]] + _RANK_POWER[board[k]]
                bs = _SUIT_BIT[board[i]] & _SUIT_BIT[board[j]] & _SUIT_BIT[board[k]]
                for p in range(10):
                    value = table[int((bs & suits[p]) != 0), br + ranks[p]]
                    if value > best:
                        best = value
    return best


@njit
def _fast_score(hole, board, table):
    ranks, suits = _pairs(hole)
    return _score_pairs(ranks, suits, board, len(board), table)


@njit
def _random_card(state):
    # Per-call PRNG state, never a global stream carried between halves.
    state ^= state << np.uint64(13)
    state ^= state >> np.uint64(7)
    state ^= state << np.uint64(17)
    return state, int(state % np.uint64(36))


@njit
def _sample(hole, board, count, runouts, seed, table, preflop):
    visible = len(board)
    known = np.uint64(0)
    for c in hole:
        known |= np.uint64(1) << np.uint64(c)
    for c in board:
        known |= np.uint64(1) << np.uint64(c)
    state = np.uint64(seed)
    hr, hs = _pairs(hole)
    opponents = np.empty((count, 5), dtype=np.int32)
    scores = np.zeros((count, 4), dtype=np.float64)
    outcomes = np.empty(count, dtype=np.float64)
    future = np.empty(5, dtype=np.int32)
    for i in range(visible):
        future[i] = board[i]
    for n in range(count):
        used = known
        for i in range(5):
            while True:
                state, card = _random_card(state)
                bit = np.uint64(1) << np.uint64(card)
                if not used & bit:
                    break
            opponents[n, i] = card
            used |= bit
        other = opponents[n]
        ranks, suits = _pairs(other)
        scores[n, 0] = preflop[_index(other)]
        for street in range(1, 4):
            length = street + 2
            if length <= visible:
                scores[n, street] = _score_pairs(ranks, suits, future, length, table)
        won = 0.0
        for run in range(runouts):
            run_used = used
            for i in range(visible, 5):
                while True:
                    state, card = _random_card(state)
                    bit = np.uint64(1) << np.uint64(card)
                    if not run_used & bit:
                        break
                future[i] = card
                run_used |= bit
            mine = _score_pairs(hr, hs, future, 5, table)
            theirs = _score_pairs(ranks, suits, future, 5, table)
            won += 1.0 if mine > theirs else (0.5 if mine == theirs else 0.0)
        outcomes[n] = won / runouts
    return opponents, scores, outcomes


_DATA = Path(__file__).resolve().parent / 'data' / 'preflop.npy'
if _DATA.exists():
    _PREFLOP = np.load(_DATA, allow_pickle=False)
elif os.environ.get('QUADJ_PRECOMPUTE') == '1':
    _PREFLOP = np.full(376992, 0.5, dtype=np.float32)
else:
    raise FileNotFoundError('Missing data/preflop.npy; include the data directory with agent.py')
if _PREFLOP.shape != (376992,) or _PREFLOP.dtype != np.float32 or not np.isfinite(_PREFLOP).all():
    raise ValueError('Invalid preflop equity table')
# Force compilation before serving requests. No compilation is charged to a half.
_sample(np.array([0, 5, 10, 15, 20], dtype=np.int32),
        np.array([24, 29, 34], dtype=np.int32), 1, 1, np.uint64(1), _SCORE, _PREFLOP)
_fast_score(np.array([0, 5, 10, 15, 20], dtype=np.int32),
            np.array([24, 29, 34], dtype=np.int32), _SCORE)


def new_half(config: AgentConfig, memory: dict) -> None:
    """Reset all learning, random state, caches, and the compute allowance."""
    memory.clear()
    memory.update(hands_played=0, config=config, rng=random.Random(19470219),
                  counts=np.zeros((4, 2, 3), dtype=float), check_evidence=np.zeros((4,2)),
                  hand=-1, seen=0, cache=None, last_obs=None, last_action=None,
                  compute_seconds=0.0, decisions=0, fallback_count=0,
                  strength_sum=0.0, strength_count=0, net=0, simulation_modes={})


def _observe(obs, memory):
    if memory['hand'] != obs.hand_index:
        memory.update(hand=obs.hand_index, seen=0, cache=None)
    # Replay public bets to distinguish a check from a call and an opening
    # bet from a re-raise. Never consult the deal or future board cards.
    config = memory['config']
    bets = [config.small_blind if obs.is_button else config.big_blind,
            config.big_blind if obs.is_button else config.small_blind]
    street, raises = 0, 0
    total = bets.copy()
    for i, entry in enumerate(obs.action_history):
        st = int(entry.street)
        if st != street:
            bets, street, raises = [0, 0], st, 0
        seat = 0 if entry.is_me else 1
        facing = int(bets[1 - seat] > bets[seat])
        can_raise = (raises < memory['config'].raise_cap and
                     total[1 - seat] < memory['config'].starting_stack and
                     memory['config'].starting_stack - total[seat] > max(0, bets[1-seat] - bets[seat]))
        if not entry.is_me and i >= memory['seen'] and can_raise:
            kind = 0 if entry.action == Action.FOLD else (2 if entry.action in (Action.RAISE_HALF, Action.RAISE_POT) else 1)
            memory['counts'][st, facing, kind] += 1
        if entry.action in (Action.RAISE_HALF, Action.RAISE_POT):
            raises += 1
        bets[seat] = entry.street_total
        total[seat] += entry.amount
    memory['seen'] = len(obs.action_history)


def _rates(memory, street, facing):
    counts = memory['counts']
    # Share information between postflop streets, with modest street-specific weight.
    if street == 0:
        c = counts[0, facing] + 0.18 * counts[1:, facing].sum(axis=0)
    else:
        c = counts[1:, facing].sum(axis=0) + counts[street, facing]
    prior = np.array([2.4, 3.6, 2.0]) if facing else np.array([0., 5., 3.])
    p = (c + prior) / (c.sum() + prior.sum())
    return p


def _percentile(values):
    ordered = np.sort(values)
    return (np.searchsorted(ordered, values, 'left') + np.searchsorted(ordered, values, 'right')) / (2.0 * len(values))


def _range_weights(obs, memory, scores):
    weights = np.ones(len(scores))
    pct = [_compact_percentile(scores[:, st]) for st in range(int(obs.street) + 1)]
    config = memory['config']
    bets = [config.small_blind if obs.is_button else config.big_blind,
            config.big_blind if obs.is_button else config.small_blind]
    street = 0
    for entry in obs.action_history:
        st = int(entry.street)
        if st != street:
            bets, street = [0, 0], st
        seat = 0 if entry.is_me else 1
        facing = int(bets[1 - seat] > bets[seat])
        if not entry.is_me:
            p = _rates(memory, st, facing)
            aggressive = p[2]
            # Frequent aggression carries less information about card strength.
            selective = max(0.0, min(1.0, (0.78 - aggressive) / 0.50))
            if memory['strength_count'] >= 10:
                mean = (memory['strength_sum'] + 6.0) / (memory['strength_count'] + 8.0)
                selective *= max(0.08, min(1.0, (mean - 0.48) / 0.23))
            strength = pct[st]
            if entry.action in (Action.RAISE_HALF, Action.RAISE_POT):
                threshold = min(0.93, 1.0 - aggressive + (0.06 if facing else 0.0))
                likelihood = 0.09 + 0.91 / (1.0 + np.exp(-12.0 * (strength - threshold)))
                weights *= (1.0 - selective) + selective * likelihood
            elif facing:
                threshold = min(0.65, p[0])
                likelihood = 0.15 + 0.85 / (1.0 + np.exp(-10.0 * (strength - threshold)))
                weights *= (1.0 - selective) + selective * likelihood
            else:
                bet_likelihood = 0.09 + 0.91 / (1.0 + np.exp(-12.0 * (strength - (1.0-aggressive))))
                old_check = 1.0 - selective * .55 * strength ** 4
                new_check = 1.0 - selective * bet_likelihood
                information = _check_information(memory,st) if st else .5
                weights *= (1-information)*old_check + information*new_check
        bets[seat] = entry.street_total
    weights = np.maximum(weights, 1e-5)
    return weights / weights.sum(), pct[-1]


@njit
def _pair_board(board, length, table):
    result = np.zeros((36,36),dtype=np.int32)
    occupied = np.uint64(0)
    for i in range(length):
        occupied |= np.uint64(1) << np.uint64(board[i])
    for a in range(35):
        if occupied & (np.uint64(1)<<np.uint64(a)):
            continue
        for b in range(a+1,36):
            if occupied & (np.uint64(1)<<np.uint64(b)):
                continue
            hr = _RANK_POWER[a]+_RANK_POWER[b]
            hs = _SUIT_BIT[a]&_SUIT_BIT[b]
            best = 0
            for i in range(length-2):
                for j in range(i+1,length-1):
                    for k in range(j+1,length):
                        br = _RANK_POWER[board[i]]+_RANK_POWER[board[j]]+_RANK_POWER[board[k]]
                        bs = _SUIT_BIT[board[i]]&_SUIT_BIT[board[j]]&_SUIT_BIT[board[k]]
                        score = table[int((bs&hs)!=0),hr+br]
                        if score>best:
                            best=score
            result[a,b]=result[b,a]=best
    return result


@njit
def _from_pair_board(hole, lookup):
    best=0
    for i in range(4):
        for j in range(i+1,5):
            value=lookup[hole[i],hole[j]]
            if value>best:
                best=value
    return best


@njit
def _shared_sample(hole, board, count, flop_boards, seed, table, preflop):
    """Share board evaluations across hands; enumerate all turn runouts."""
    visible=len(board)
    known=np.uint64(0)
    for c in hole:
        known |= np.uint64(1)<<np.uint64(c)
    for c in board:
        known |= np.uint64(1)<<np.uint64(c)
    state=np.uint64(seed)
    opponents=np.empty((count,5),dtype=np.int32)
    masks=np.empty(count,dtype=np.uint64)
    scores=np.zeros((count,4))
    outcomes=np.zeros(count)
    visits=np.zeros(count)
    for n in range(count):
        used=known
        for i in range(5):
            while True:
                state,c=_random_card(state)
                bit=np.uint64(1)<<np.uint64(c)
                if not used&bit:
                    break
            opponents[n,i]=c
            used |= bit
        masks[n]=used
        scores[n,0]=preflop[_index(opponents[n])]
    for st in range(1,4):
        length=st+2
        if length<=visible:
            lookup=_pair_board(board,length,table)
            for n in range(count):
                scores[n,st]=_from_pair_board(opponents[n],lookup)
    if visible==5:
        mine=_from_pair_board(hole,lookup)
        for n in range(count):
            value=scores[n,3]
            outcomes[n]=1. if mine>value else .5 if mine==value else 0.
        return opponents,scores,outcomes
    future=np.empty(5,dtype=np.int32)
    for i in range(visible):
        future[i]=board[i]
    boards=36 if visible==4 else 1296 if flop_boards == 0 else flop_boards
    for run in range(boards):
        used=known
        future_mask=np.uint64(0)
        if visible==4:
            c=run
            bit=np.uint64(1)<<np.uint64(c)
            if used&bit:
                continue
            future[4]=c
            future_mask=bit
        elif flop_boards == 0 and visible == 3:
            a=run//36; b=run%36
            bits=(np.uint64(1)<<np.uint64(a))|(np.uint64(1)<<np.uint64(b))
            if a>=b or known&bits:
                continue
            future[3]=a; future[4]=b
            future_mask=bits
        else:
            for i in range(visible,5):
                while True:
                    state,c=_random_card(state)
                    bit=np.uint64(1)<<np.uint64(c)
                    if not used&bit:
                        break
                future[i]=c
                used |= bit
                future_mask |= bit
        lookup=_pair_board(future,5,table)
        mine=_from_pair_board(hole,lookup)
        for n in range(count):
            if masks[n]&future_mask:
                continue
            value=_from_pair_board(opponents[n],lookup)
            outcomes[n]+=1. if mine>value else .5 if mine==value else 0.
            visits[n]+=1
    for n in range(count):
        if visits[n]:
            outcomes[n]/=visits[n]
        else:
            # Very small flop batches may all collide with one candidate.
            # Complete legal boards directly for that candidate instead.
            ranks,suits=_pairs(opponents[n])
            hr,hs=_pairs(hole)
            used=masks[n]
            for i in range(visible,5):
                while True:
                    state,c=_random_card(state)
                    bit=np.uint64(1)<<np.uint64(c)
                    if not used&bit:
                        break
                future[i]=c
                used |= bit
            mine=_score_pairs(hr,hs,future,5,table)
            value=_score_pairs(ranks,suits,future,5,table)
            outcomes[n]=1. if mine>value else .5 if mine==value else 0.
    return opponents,scores,outcomes


_shared_sample(np.array([0,5,10,15,20],dtype=np.int32),
               np.array([24,29,34],dtype=np.int32),1,1,np.uint64(1),_SCORE,_PREFLOP)


# Compact ranks make exact river percentiles inexpensive; packed scores remain
# authoritative. This index is static and contains no match information.
from evaluator import get_table as _get_score_table
_score_values=np.unique(np.fromiter(_get_score_table().values(),dtype=np.int32))
_SCORE_ORDINAL=np.zeros(int(_score_values[-1])+1,dtype=np.uint16)
_SCORE_ORDINAL[_score_values]=np.arange(1,len(_score_values)+1,dtype=np.uint16)
_pf_values=np.unique(_PREFLOP).astype(np.float64)
_pf_keys=np.rint(_pf_values*16777216).astype(np.int32)
_PF_ORDINAL=np.zeros(16777217,dtype=np.uint16)
_PF_COMPACT_OK=len(np.unique(_pf_keys))==len(_pf_keys) and len(_pf_keys)<65535
if _PF_COMPACT_OK:
    _PF_ORDINAL[_pf_keys]=np.arange(1,len(_pf_keys)+1,dtype=np.uint16)



@njit
def _river_all(hole,board,table,preflop):
    blocked=np.zeros(36,dtype=np.uint8)
    for c in hole:blocked[c]=1
    for c in board:blocked[c]=1
    remaining=np.empty(26,dtype=np.int32)
    n=0
    for c in range(36):
        if not blocked[c]:remaining[n]=c;n+=1
    count=_BINOM[26,5]
    opponents=np.empty((count,5),dtype=np.int32)
    scores=np.empty((count,4),dtype=np.float64)
    outcomes=np.empty(count)
    index=0
    for i in range(22):
        a=remaining[i]
        for j in range(i+1,23):
            b=remaining[j]
            for k in range(j+1,24):
                c=remaining[k]
                for l in range(k+1,25):
                    d=remaining[l]
                    for m in range(l+1,26):
                        e=remaining[m]
                        opponents[index,0]=a;opponents[index,1]=b;opponents[index,2]=c
                        opponents[index,3]=d;opponents[index,4]=e
                        key=_BINOM[a,1]+_BINOM[b,2]+_BINOM[c,3]+_BINOM[d,4]+_BINOM[e,5]
                        scores[index,0]=preflop[key]
                        index+=1
    for st in range(1,4):
        lookup=_pair_board(board,st+2,table)
        for row in range(count):scores[row,st]=_from_pair_board(opponents[row],lookup)
    mine=_from_pair_board(hole,lookup)
    for row in range(count):
        value=scores[row,3]
        outcomes[row]=1. if mine>value else .5 if mine==value else 0.
    return opponents,scores,outcomes


_river_all(np.array([0,5,10,15,20],dtype=np.int32),
           np.array([24,29,34,1,6],dtype=np.int32),_SCORE,_PREFLOP)


def _compact_percentile(values):
    if len(values)<8192:
        return _percentile(values)
    if values.max()<=1. and values.min()>=0.:
        if not _PF_COMPACT_OK:return _percentile(values)
        bins=_PF_ORDINAL[np.rint(values*16777216).astype(np.int32)]
        if np.any(bins==0):return _percentile(values)
    elif values.min()>=0 and values.max()<len(_SCORE_ORDINAL):
        bins=_SCORE_ORDINAL[values.astype(np.int32)]
        if np.any(bins==0):return _percentile(values)
    else:
        return _percentile(values)
    counts=np.bincount(bins)
    cumulative=np.cumsum(counts)
    return (cumulative[bins]-.5*counts[bins])/len(values)


def _simulation(obs, memory):
    key = (obs.hand_index, obs.hole_cards, obs.board)
    cached = memory['cache']
    if cached is not None and cached['key'] == key:
        return cached
    # Keep substantial time for HTTP overhead and slower tournament hardware.
    hands = max(1, memory['config'].num_hands)
    allowance = memory['config'].time_bank_seconds * 0.40 / hands
    spent_per_hand = memory['compute_seconds'] / max(1, obs.hand_index + 1)
    scale = min(1.0, allowance / max(allowance, spent_per_hand))
    n = max(96, int((768 if obs.street != Street.RIVER else 1536) * scale))
    hole = np.asarray(obs.hole_cards, dtype=np.int32)
    board = np.asarray(obs.board, dtype=np.int32)
    if len(board)==5 and scale>.55:
        other,scores,outcomes=_river_all(hole,board,_SCORE,_PREFLOP)
        mode='exact_river'
    elif scale<.5:
        other,scores,outcomes=_sample(hole,board,n,3 if len(board)<5 else 1,
                                      np.uint64(memory['rng'].getrandbits(63)|1),_SCORE,_PREFLOP)
        mode='sampled_budget'
    else:
        other,scores,outcomes=_shared_sample(hole,board,n,0,
                                      np.uint64(memory['rng'].getrandbits(63)|1),_SCORE,_PREFLOP)
        mode='full_runouts'
    memory['simulation_modes'][mode]=memory['simulation_modes'].get(mode,0)+1
    cached = dict(key=key, opponents=other, scores=scores, outcomes=outcomes, mode=mode)
    memory['cache'] = cached
    return cached


# Tuned offline; only public observations influence decisions during a match.
_POLICY = dict(open_button=.48, reraise_value=.57, preflop_penalty=.035,
               realization=1.0, raise_margin=1.0, check_center=.54, check_prior=12.0, street_sharing=1.0)


def _decide(obs, memory):
    _observe(obs, memory)
    st = int(obs.street)
    free = obs.to_call == 0
    raising = Action.RAISE_POT in obs.legal_actions
    p_free = _rates(memory, st, 0)
    p_facing = _rates(memory, st, 1)
    if st == 0:
        equity = float(_PREFLOP[_index(np.asarray(obs.hole_cards, dtype=np.int32))])
        # Preflop equities are precomputed from random legal deals. Raise
        # histories then shift the estimate toward the opponent's stronger range.
        opp_raises = sum(not a.is_me and a.action in (Action.RAISE_HALF, Action.RAISE_POT) for a in obs.action_history)
        selectivity = max(0.0, (0.78 - p_facing[2]) / 0.55)
        adjusted = equity - selectivity * min(0.14, _POLICY['preflop_penalty'] * opp_raises)
        if raising:
            if obs.raises_this_street == 0:
                if (obs.is_button and equity >= _POLICY['open_button']) or equity >= 0.56:
                    return Action.RAISE_POT
                # Steal against observed over-folding without risking a large pot.
                if p_facing[0] > 0.63:
                    return Action.RAISE_HALF
            elif adjusted > (_POLICY['reraise_value'] if p_facing[2] < 0.65 else 0.525):
                return Action.RAISE_POT
        if free:
            return Action.CHECK_CALL
        cost = min(obs.to_call, obs.my_stack)
        odds = cost / (obs.pot + cost)
        # Against relentless raisers, marginal preflop calls commit the stack
        # over subsequent raises, so require near break-even all-in equity.
        if p_facing[2] > 0.78 and obs.opp_stack > 0:
            threshold = min(0.495, (obs.my_stack / (obs.pot + 2 * obs.my_stack - obs.to_call)))
        else:
            spr = min(obs.my_stack - cost, obs.opp_stack) / max(1, obs.pot + cost)
            threshold = odds + (0.10 if spr > 2 else 0.045 if spr > 0.5 else 0.0)
        return Action.CHECK_CALL if adjusted >= threshold else Action.FOLD
    simulation = _simulation(obs, memory)
    weights, strength = _range_weights(obs, memory, simulation['scores'])
    outcomes = simulation['outcomes']
    equity = float(np.dot(weights, outcomes))
    cost = min(obs.to_call, obs.my_stack)
    odds = cost / max(1, obs.pot + cost)
    spr = max(0, min(obs.my_stack - cost, obs.opp_stack)) / max(1, obs.pot + cost)
    # Future betting reduces the value of weak draws out of position.
    reserve = _POLICY['realization'] * (0.045 if not obs.is_button else 0.025) * min(1.0, spr) if st < 3 else 0.0
    if not free and equity < odds + reserve:
        return Action.FOLD
    if not raising:
        return Action.CHECK_CALL
    # Approximate the continuing range for each available size. Large bets
    # must earn their chips against hands that actually call, not folded hands.
    base_ev = equity * (obs.pot + cost) - cost
    best_action, best_ev = Action.CHECK_CALL, base_ev
    for action in (Action.RAISE_HALF, Action.RAISE_POT):
        if action not in obs.legal_actions:
            continue
        invest = obs.raise_to[action] - obs.my_bet
        reply = min(obs.opp_stack, max(0, obs.raise_to[action] - obs.opp_bet))
        risk_ratio = reply / max(1, obs.pot + invest + reply)
        fold_rate = p_facing[0]
        if not free:
            fold_rate *= 0.55
        fold_rate *= 0.85 + risk_ratio
        # Fit continuation strength to observed folds. Calling stations and
        # maniacs retain almost their entire range.
        selectivity = max(0.0, min(1.0, (0.80 - p_facing[2]) / 0.55))
        continue_p = 1.0 - fold_rate * ((1.0 - selectivity) + selectivity * 2.0 * (1.0 - strength))
        continue_p = np.clip(continue_p, 0.03, 1.0)
        continuing = weights * continue_p
        call_prob = float(continuing.sum())
        eq_called = float(np.dot(continuing, outcomes) / call_prob)
        ev = (1 - call_prob) * obs.pot + call_prob * (eq_called * (obs.pot + invest + reply) - invest)
        # A one-step estimate overvalues bluffs that can be re-raised and
        # medium hands with several streets still to play.
        if st < 3:
            ev -= call_prob * invest * max(0.0, 0.62 - eq_called) * (0.70 if spr > 1 else 0.25)
        margin = _POLICY['raise_margin'] * max(0.35, obs.pot * (0.035 if st < 3 else 0.018))
        if ev > best_ev + margin:
            best_action, best_ev = action, ev
    return best_action


def choose_action(obs: Observation, memory: dict) -> Action:
    """Return a legal action using equity, public betting, and half-local learning."""
    start = time.perf_counter()
    try:
        action = _decide(obs, memory)
    except (ArithmeticError, ValueError, IndexError, KeyError):
        # A legal conservative fallback, counted so tests can detect its use.
        memory['fallback_count'] = memory.get('fallback_count', 0) + 1
        action = Action.CHECK_CALL if obs.to_call == 0 else Action.FOLD
    memory['last_obs'], memory['last_action'] = obs, action
    memory['decisions'] += 1
    memory['compute_seconds'] += time.perf_counter() - start
    return action if action in obs.legal_actions else Action.CHECK_CALL


def _learn_checks(result, memory):
    """Learn from revealed cards only; shrink sparse evidence toward the prior."""
    obs, cache = memory.get('last_obs'), memory.get('cache')
    if not result.opp_hole or obs is None or cache is None or obs.hand_index != result.hand_index or cache['key'][0] != result.hand_index:
        return
    other = np.asarray(result.opp_hole,dtype=np.int32)
    cfg = memory['config']
    bets = [cfg.small_blind if obs.is_button else cfg.big_blind,
            cfg.big_blind if obs.is_button else cfg.small_blind]
    street = 0
    learned = set()
    for entry in obs.action_history:
        st = int(entry.street)
        if st != street:
            bets,street = [0,0],st
        seat = 0 if entry.is_me else 1
        if st and not entry.is_me and entry.action == Action.CHECK_CALL and bets[0] <= bets[1] and st not in learned:
            learned.add(st)
            actual = _fast_score(other,np.asarray(obs.board[:st+2],dtype=np.int32),_SCORE)
            pool = cache['scores'][:,st]
            percentile = float(np.mean(pool < actual)+.5*np.mean(pool == actual))
            memory['check_evidence'][st,0] += percentile
            memory['check_evidence'][st,1] += 1
        bets[seat] = entry.street_total


def _check_information(memory, street):
    # Showdown samples are selected by the betting. This is cautious evidence
    # of slow-playing, not an unbiased estimate of the entire checking range.
    evidence = _POLICY['street_sharing']*memory['check_evidence'][1:].sum(axis=0) + memory['check_evidence'][street]
    mean = (evidence[0]+_POLICY['check_prior']*.50)/(evidence[1]+_POLICY['check_prior'])
    return max(0.,min(1.,(_POLICY['check_center']-mean)/.12))


def on_hand_end(result: HandResult, memory: dict) -> None:
    """Learn terminal responses, which do not appear in the next observation."""
    _learn_checks(result,memory)
    memory['hands_played'] += 1
    memory['net'] += result.my_net
    obs, action = memory.get('last_obs'), memory.get('last_action')
    if obs is None or obs.hand_index != result.hand_index:
        return
    if (action in (Action.RAISE_HALF, Action.RAISE_POT)
            and obs.raises_this_street + 1 < memory['config'].raise_cap
            and obs.my_stack > obs.raise_to[action] - obs.my_bet
            and obs.opp_stack > obs.raise_to[action] - obs.opp_bet):
        if not result.went_to_showdown and result.winner == 'me':
            memory['counts'][int(obs.street), 1, 0] += 1
        elif result.went_to_showdown:
            memory['counts'][int(obs.street), 1, 1] += 1
    cached = memory.get('cache')
    if result.opp_hole and cached is not None and cached['key'][0] == result.hand_index:
        other = np.asarray(result.opp_hole, dtype=np.int32)
        for st in set(int(a.street) for a in obs.action_history if not a.is_me and a.action in (Action.RAISE_HALF, Action.RAISE_POT)):
            if st == 0:
                value = float(_PREFLOP[_index(other)])
            else:
                value = _fast_score(other, np.asarray(obs.board[:st+2], dtype=np.int32), _SCORE)
            pool = cached['scores'][:, st]
            memory['strength_sum'] += float(np.mean(pool < value) + 0.5 * np.mean(pool == value))
            memory['strength_count'] += 1

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
