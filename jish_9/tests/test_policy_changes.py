from dataclasses import replace
import numpy as np
import pytest
import agent
from game import Action, AgentConfig, Game, Street, make_deal


def test_repop_guard_requires_observed_repeated_aggression(monkeypatch):
    monkeypatch.setattr(agent,'_AVOID_MARGINAL_REPOP',True)
    monkeypatch.setattr(agent,'_PASSIVE_ISOLATION',False)
    memory={};agent.new_half(AgentConfig(),memory)
    assert agent._preflop_open_limits(memory,np.array([0.,.05,.95]),.48)==(.48,.56)
    memory['counts'][0,1,2]=100
    assert agent._preflop_open_limits(memory,np.array([0.,.05,.95]),.48)==(.495,.56)
    assert agent._preflop_open_limits(memory,np.array([.2,.5,.3]),.48)==(.48,.56)


def test_passive_value_requires_calls_and_checks_not_merely_checks(monkeypatch):
    monkeypatch.setattr(agent,'_AVOID_MARGINAL_REPOP',False)
    monkeypatch.setattr(agent,'_PASSIVE_ISOLATION',True)
    memory={};agent.new_half(AgentConfig(),memory)
    facing=np.array([0.,1.,0.])
    memory['counts'][0,0,1]=100
    assert agent._preflop_open_limits(memory,facing,.48)==(.48,.56)
    memory['counts'][0,1,1]=100
    assert agent._preflop_open_limits(memory,facing,.48)==(.48,.52)
    memory['counts'][0,1,0]=100
    assert agent._preflop_open_limits(memory,facing,.48)==(.48,.56)
    agent.new_half(AgentConfig(),memory)
    assert agent._preflop_open_limits(memory,facing,.48)==(.48,.56)


def test_adaptation_requires_evidence_and_observed_pressure(monkeypatch):
    monkeypatch.setattr(agent,'_STYLE_ADAPTIVE',True)
    monkeypatch.setattr(agent,'_BUTTON_OPEN',.56)
    monkeypatch.setattr(agent,'_CALL_DISCOUNT',.06)
    memory={};agent.new_half(AgentConfig(),memory)
    facing=np.array([.2,.5,.3]);pressure=np.array([0.,.2,.8])
    opening,discount=agent._policy_adjustments(memory,facing,pressure,3)
    assert opening==.48 and discount==0.
    memory['counts'][0]=100
    memory['counts'][1:,0]=100
    opening,discount=agent._policy_adjustments(memory,facing,pressure,3)
    assert .48<opening<=.56 and 0<discount<=.06
    _,passive=agent._policy_adjustments(memory,facing,np.array([0.,.99,.01]),3)
    assert passive==0.
    folding,_=agent._policy_adjustments(memory,np.array([.8,.1,.1]),pressure,0)
    assert folding==.48
    agent.new_half(AgentConfig(),memory)
    assert agent._policy_adjustments(memory,facing,pressure,3)==(.48,0.)


def test_button_open_threshold_does_not_tighten_big_blind(monkeypatch):
    monkeypatch.setattr(agent,'_STYLE_ADAPTIVE',False)
    monkeypatch.setattr(agent,'_BUTTON_OPEN',.62)
    monkeypatch.setattr(agent,'_index',lambda hole:0)
    monkeypatch.setattr(agent,'_PREFLOP',{0:.58})
    memory={};agent.new_half(AgentConfig(),memory)
    obs=Game(make_deal('open',0),0).observation(0)
    assert agent._decide(obs,memory)==Action.CHECK_CALL
    assert agent._decide(replace(obs,is_button=False),memory)==Action.RAISE_POT


def test_call_adjustment_is_bounded_and_does_not_force_any_call(monkeypatch):
    monkeypatch.setattr(agent,'_STYLE_ADAPTIVE',False)
    monkeypatch.setattr(agent,'_CALL_DISCOUNT',.08)
    memory={};agent.new_half(AgentConfig(),memory)
    obs=Game(make_deal('defense',0),0).observation(0)
    obs=replace(obs,street=Street.RIVER,pot=20,to_call=10,
                legal_actions=(Action.FOLD,Action.CHECK_CALL))
    monkeypatch.setattr(agent,'_range_weights',lambda *args:(np.ones(1),np.ones(1)))
    monkeypatch.setattr(agent,'_simulation',lambda *args:dict(scores=np.zeros((1,4)),outcomes=np.array([.20])))
    assert agent._decide(obs,memory)==Action.FOLD
    monkeypatch.setattr(agent,'_simulation',lambda *args:dict(scores=np.zeros((1,4)),outcomes=np.array([.26])))
    assert agent._decide(obs,memory)==Action.CHECK_CALL
    monkeypatch.setattr(agent,'_CALL_DISCOUNT',0.)
    assert agent._decide(obs,memory)==Action.FOLD


@pytest.mark.parametrize('stack',[3,5,9,80])
@pytest.mark.parametrize('style',['pot','station','fold','switch'])
def test_legal_actions_with_short_stacks_caps_and_changing_styles(stack,style,monkeypatch):
    import game as rules
    monkeypatch.setattr(rules,'STARTING_STACK',stack)
    memory={};agent.new_half(AgentConfig(starting_stack=stack,num_hands=24),memory)
    for hand in range(24):
        game=Game(make_deal('jish9-edge',hand),hand%2,hand)
        while not game.is_terminal:
            obs=game.observation(game.to_act)
            if game.to_act==hand%2:
                action=agent.choose_action(obs,memory)
            else:
                active=('pot' if hand%2 else 'station') if style=='switch' else style
                action=Action.CHECK_CALL
                if active=='pot' and Action.RAISE_POT in obs.legal_actions:action=Action.RAISE_POT
                elif active=='fold' and obs.to_call:action=Action.FOLD
            assert action in obs.legal_actions
            game.apply(action)
        agent.on_hand_end(game.hand_result(hand%2),memory)
    assert memory['fallback_count']==0
