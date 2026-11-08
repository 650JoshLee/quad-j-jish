"""Independent transition and strategic regression tests for jish_11."""
import importlib.util
from pathlib import Path
import random
from dataclasses import replace
import numpy as np
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import agent
from game import Game,make_deal,Action,AgentConfig,Street


def test_reraise_costs_match_actual_judge():
    rng=random.Random(20261111);count=0
    for hand in range(150):
        g=Game(make_deal('reraise-rules',hand),hand%2)
        while not g.is_terminal:
            seat=g.to_act;obs=g.observation(seat)
            for action in [Action.RAISE_HALF,Action.RAISE_POT]:
                if action not in g.legal_actions():continue
                raised=g.clone();raised.apply(action)
                for fraction,response in [(.5,Action.RAISE_HALF),(1.,Action.RAISE_POT)]:
                    if raised.is_terminal or response not in raised.legal_actions():continue
                    other=raised.clone();other.apply(response)
                    assert agent._reraise_terms(obs,action,fraction)==(
                        obs.my_stack-raised.stacks[seat],obs.opp_stack-other.stacks[1-seat],
                        min(other.stacks[seat],other.bets[1-seat]-other.bets[seat]))
                    count+=1
            g.apply(rng.choice(g.legal_actions()))
    assert count>300


def test_size_learning_separates_responses_and_shrinks_sparse_evidence():
    memory={};agent.new_half(AgentConfig(),memory)
    obs=Game(make_deal('sizes',0),0).observation(0)
    small=agent._response_rates(obs,memory,Action.RAISE_HALF)
    assert np.allclose(small,agent._rates(memory,0,1))
    memory['size_counts'][0,0]=[200,0,0]
    memory['size_counts'][0,1]=[0,200,0]
    assert agent._response_rates(obs,memory,Action.RAISE_HALF)[0]>.8
    assert agent._response_rates(obs,memory,Action.RAISE_POT)[1]>.8
    agent.new_half(AgentConfig(),memory)
    assert not memory['size_counts'].any()


def test_observed_response_is_counted_once_in_actual_size_bucket():
    m={};agent.new_half(AgentConfig(),m)
    g=Game(make_deal('count-size',0),0)
    g.apply(Action.RAISE_HALF);g.apply(Action.RAISE_POT)
    obs=g.observation(0)
    agent._observe(obs,m);agent._observe(obs,m)
    assert m['size_counts'][0,0,2]==1
    assert m['size_counts'].sum()==1


def river_obs():
    obs=Game(make_deal('bluff',0),0).observation(0)
    return replace(obs,street=Street.RIVER,pot=40,my_bet=0,opp_bet=1,to_call=1,
                   my_stack=60,opp_stack=59,raises_this_street=1,
                   board=(20,24,28,32,35),hole_cards=(0,4,8,12,16),
                   legal_actions=tuple(Action),raise_to={Action.RAISE_HALF:21,Action.RAISE_POT:42})


def test_low_equity_raise_considered_against_extreme_folding(monkeypatch):
    obs=river_obs();m={};agent.new_half(AgentConfig(),m)
    monkeypatch.setattr(agent,'_observe',lambda *args:None)
    monkeypatch.setattr(agent,'_rates',lambda *args:np.array([.99,.01,0.]))
    monkeypatch.setattr(agent,'_simulation',lambda *args:dict(scores=np.zeros((100,4)),outcomes=np.zeros(100)))
    monkeypatch.setattr(agent,'_range_weights',lambda *args:(np.full(100,.01),np.linspace(0,1,100)))
    monkeypatch.setattr(agent,'_SIZE_LEARNING',False)
    monkeypatch.setattr(agent,'_RERAISE_BLEND',0.)
    monkeypatch.setattr(agent,'_BLUFF_RAISES',False)
    assert agent._decide(obs,m)==Action.FOLD
    monkeypatch.setattr(agent,'_BLUFF_RAISES',True)
    assert agent._decide(obs,m) in (Action.RAISE_HALF,Action.RAISE_POT)
    monkeypatch.setattr(agent,'_rates',lambda *args:np.array([0.,1.,0.]))
    assert agent._decide(obs,m)==Action.FOLD


def test_reraise_model_values_nuts_and_weak_hand_differently():
    obs=river_obs();weights=np.ones(10)/10;strength=np.linspace(0,1,10)
    no_raise=np.array([0.,1.,0.]);always_raise=np.array([0.,0.,1.])
    strong=agent._raise_response_ev(obs,Action.RAISE_HALF,weights,strength,np.ones(10),always_raise,0.)
    call=agent._raise_response_ev(obs,Action.RAISE_HALF,weights,strength,np.ones(10),no_raise,0.)
    assert strong>call
    weak=agent._raise_response_ev(obs,Action.RAISE_HALF,weights,strength,np.zeros(10),always_raise,0.)
    assert weak==-(obs.raise_to[Action.RAISE_HALF]-obs.my_bet)


def test_cap_removes_unavailable_reraise_branch():
    obs=replace(river_obs(),raises_this_street=3)
    args=(obs,Action.RAISE_HALF,np.ones(10)/10,np.linspace(0,1,10),np.linspace(0,1,10))
    assert agent._raise_response_ev(*args,np.array([0.,1.,0.]),1.)==agent._raise_response_ev(*args,np.array([0.,0.,1.]),1.)
