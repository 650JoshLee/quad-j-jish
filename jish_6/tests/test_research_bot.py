import random
from itertools import combinations
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
import agent
from evaluator import omaha_score,score_five,cards_from_str
from game import AgentConfig,Game,Action,make_deal


def test_acceleration_matches_official_exact_two_plus_three_rule():
    rng=random.Random(610079)
    for _ in range(1800):
        cards=rng.sample(range(36),10);h=np.array(cards[:5],np.int32)
        for length in [3,4,5]:
            b=np.array(cards[5:5+length],np.int32)
            expected=max(score_five(tuple(x)+tuple(y)) for x in combinations(h,2) for y in combinations(b,3))
            assert agent._value(h,b,agent._GRID)==expected


def test_one_private_heart_cannot_make_a_flush():
    h=np.array(cards_from_str('Ah Kd 6c 7d 8s'),np.int32)
    b=np.array(cards_from_str('Qh Jh Th 9c 6d'),np.int32)
    assert agent._value(h,b,agent._GRID)==omaha_score(h.tolist(),b.tolist())
    assert agent._value(h,b,agent._GRID)>>20 not in (6,8)
    assert agent._potential(h,b[:3])<.5


def test_complete_board_samples_exclude_every_known_card_and_score_exactly():
    h=np.array([0,5,10,15,20],np.int32);b=np.array([24,29,34,3,9],np.int32)
    others,states,draws,wins=agent._trials(h,b,160,1,731,agent._GRID,agent._OPENING)
    own=omaha_score(h.tolist(),b.tolist())
    for hand,win in zip(others,wins):
        assert len(set(hand))==5 and not set(hand)&(set(h)|set(b))
        theirs=omaha_score(hand.tolist(),b.tolist())
        assert win==(1. if own>theirs else .5 if own==theirs else 0.)


def test_opening_model_is_new_complete_and_suit_invariant():
    assert agent._OPENING.shape==(376992,)
    assert .49<float(agent._OPENING.mean())<.51
    rng=random.Random(1906)
    for _ in range(200):
        h=np.array(rng.sample(range(36),5),np.int32);p=rng.sample(range(4),4)
        other=np.array([(c//4)*4+p[c%4] for c in h],np.int32)
        a=agent._OPENING[np.searchsorted(agent._MASKS,agent._key(h))]
        b=agent._OPENING[np.searchsorted(agent._MASKS,agent._key(other))]
        assert a==b


def test_half_memory_is_local_and_real_trajectories_are_legal():
    m={};agent.new_half(AgentConfig(),m)
    rng=random.Random(888)
    for hand in range(160):
        game=Game(make_deal('research-legality',hand),hand%2,hand)
        while not game.is_terminal:
            obs=game.observation(game.to_act)
            act=agent.choose_action(obs,m) if game.to_act==0 else rng.choice(obs.legal_actions)
            assert act in obs.legal_actions;game.apply(act)
        agent.on_hand_end(game.hand_result(0),m)
    assert m['hands']==160 and m['statistics'].sum()>0
    agent.new_half(AgentConfig(),m)
    assert m['hands']==0 and m['statistics'].sum()==0 and m['simulation'] is None


def test_preflop_open_is_separate_from_facing_a_voluntary_raise():
    game=Game(make_deal('opening-versus-threebet',0),0,0)
    game.apply(Action.RAISE_HALF)
    first=agent._history(game.observation(1),AgentConfig())
    assert first[0][2]==0  # Opening over a posted blind is not a 3-bet.
    game.apply(Action.RAISE_POT)
    second=agent._history(game.observation(0),AgentConfig())
    assert second[1][2]==1  # Big blind now raises against a voluntary open.
