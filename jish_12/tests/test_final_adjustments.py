"""Regression checks for conservative, context-specific exploitation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dataclasses import replace
import numpy as np
import pytest
import agent
from game import Game,make_deal,AgentConfig,Action,Street,HandResult

def setup():
 m={};agent.new_half(AgentConfig(),m)
 o=Game(make_deal('final-guards',0),0).observation(0)
 o=replace(o,street=Street.RIVER,pot=40,to_call=1,my_bet=0,opp_bet=1,my_stack=60,opp_stack=59,raises_this_street=1,
           hole_cards=(0,4,8,12,16),board=(20,24,28,32,35),legal_actions=tuple(Action),raise_to={Action.RAISE_HALF:21,Action.RAISE_POT:42})
 return o,m

def test_sparse_evidence_retains_original_rates():
 o,m=setup();m['response_counts'][3,1,0]=[8,0,0]
 assert np.array_equal(agent._conditioned_rates(o,m,Action.RAISE_HALF),agent._rates(m,3,1))
 assert not agent._supported_bluff(o,m,Action.RAISE_HALF)

def test_response_contexts_and_sizes_are_separate():
 o,m=setup();m['response_counts'][3,0,0]=[500,0,0]
 assert not agent._supported_bluff(o,m,Action.RAISE_HALF)
 m['response_counts'][3,1,0]=[500,0,0]
 assert agent._supported_bluff(o,m,Action.RAISE_HALF)
 assert not agent._supported_bluff(o,m,Action.RAISE_POT)
 assert agent._conditioned_rates(o,m,Action.RAISE_HALF)[0]>.9

def test_nonfolding_evidence_never_supports_a_pure_bluff():
 o,m=setup();m['response_counts'][3,1,0]=[0,1000,0]
 assert not agent._supported_bluff(o,m,Action.RAISE_HALF)

@pytest.mark.parametrize('success,total',[(0,1),(0,100),(1,1),(20,32),(100,100),(999,1000)])
def test_wilson_lower_is_conservative_and_bounded(success,total):
 assert 0<=agent._wilson_lower(success,total)<=success/total

def test_actual_reraise_response_counts_once_in_correct_context():
 m={};agent.new_half(AgentConfig(),m);g=Game(make_deal('context-replay',0),0)
 g.apply(Action.CHECK_CALL);g.apply(Action.RAISE_POT);g.apply(Action.RAISE_HALF);g.apply(Action.RAISE_POT)
 o=g.observation(0);agent._observe(o,m);agent._observe(o,m)
 assert m['response_counts'][0,1,0,2]==1
 assert m['response_counts'].sum()==1

def test_terminal_fold_recorded_and_reset():
 m={};agent.new_half(AgentConfig(),m);g=Game(make_deal('terminal-fold',0),0)
 o=g.observation(0);m['last_obs']=o;m['last_action']=Action.RAISE_HALF
 g.apply(Action.RAISE_HALF);g.apply(Action.FOLD);agent.on_hand_end(g.hand_result(0),m)
 assert m['response_counts'][0,1,0,0]==1
 agent.new_half(AgentConfig(),m);assert not m['response_counts'].any()

def test_capped_response_does_not_train_optional_reraise_model():
 o,m=setup();m['last_obs']=replace(o,raises_this_street=3);m['last_action']=Action.RAISE_HALF
 r=HandResult(hand_index=0,my_net=1,pot=40,went_to_showdown=False,board=o.board,opp_hole=None,winner='me')
 agent.on_hand_end(r,m);assert not m['response_counts'].any()

def test_bluff_gate_changes_action_only_with_support(monkeypatch):
 o,m=setup();monkeypatch.setattr(agent,'_observe',lambda *args:None)
 monkeypatch.setattr(agent,'_simulation',lambda *args:dict(scores=np.zeros((100,4)),outcomes=np.zeros(100)))
 monkeypatch.setattr(agent,'_range_weights',lambda *args:(np.full(100,.01),np.linspace(0,1,100)))
 monkeypatch.setattr(agent,'_rates',lambda *args:np.array([.99,.01,0.]))
 monkeypatch.setattr(agent,'_BLUFF_GATE',True)
 assert agent._decide(o,m)==Action.FOLD
 m['response_counts'][3,1,0]=[200,0,0]
 assert agent._decide(o,m)==Action.RAISE_HALF
