"""Range and legal-action regressions for extreme opponents and stack sizes."""
from dataclasses import replace
import numpy as np
import pytest
import agent
from game import Action, AgentConfig, Game, ObservedAction, Street, make_deal


def setup_river(history):
    memory = {}
    agent.new_half(AgentConfig(), memory)
    obs = Game(make_deal('extreme-range', 0), 0).observation(0)
    return memory, replace(obs, street=Street.RIVER, action_history=tuple(history))


def test_station_checks_converge_to_uninformative(monkeypatch):
    monkeypatch.setattr(agent, '_PASSIVE_CHECK', True)
    memory, obs = setup_river([ObservedAction(Street.RIVER, False, Action.CHECK_CALL, 0, 0)])
    memory['counts'][3, 0, 1] = 100000
    scores = np.tile(np.arange(100.)[:, None], (1, 4))
    weights, _ = agent._range_weights(obs, memory, scores)
    assert np.max(abs(weights-.01)) < .00001


def test_nonfolding_calls_do_not_imply_strong_cards(monkeypatch):
    monkeypatch.setattr(agent, '_CALL_EVIDENCE', True)
    memory, obs = setup_river([
        ObservedAction(Street.RIVER, True, Action.RAISE_HALF, 10, 10),
        ObservedAction(Street.RIVER, False, Action.CHECK_CALL, 10, 10),
    ])
    memory['counts'][3, 1, 1] = 100000
    weights, _ = agent._range_weights(obs, memory, np.tile(np.arange(100.)[:, None], (1, 4)))
    assert np.max(abs(weights-.01)) < .00001


def test_repeated_raises_can_be_discounted_without_erasing_first_raise(monkeypatch):
    memory, obs = setup_river([
        ObservedAction(Street.RIVER, False, Action.RAISE_HALF, 10, 10),
        ObservedAction(Street.RIVER, True, Action.RAISE_HALF, 25, 25),
        ObservedAction(Street.RIVER, False, Action.RAISE_POT, 50, 60),
    ])
    scores = np.tile(np.arange(100.)[:, None], (1, 4))
    monkeypatch.setattr(agent, '_REPEAT_EVIDENCE', 1.)
    full, _ = agent._range_weights(obs, memory, scores)
    monkeypatch.setattr(agent, '_REPEAT_EVIDENCE', .5)
    discounted, _ = agent._range_weights(obs, memory, scores)
    assert .2 < discounted[-20:].sum() < full[-20:].sum()
    assert np.isclose(discounted.sum(), 1)


def test_recent_evidence_decays_once_per_hand_and_resets(monkeypatch):
    monkeypatch.setattr(agent, '_RECENT_DECAY', .99)
    memory = {}
    agent.new_half(AgentConfig(), memory)
    memory['counts'][:] = 100
    obs = Game(make_deal('decay', 0), 0, 0).observation(0)
    agent._observe(obs, memory)
    assert np.allclose(memory['counts'], 99)
    agent._observe(obs, memory)
    assert np.allclose(memory['counts'], 99)
    agent._observe(replace(obs, hand_index=1), memory)
    assert np.allclose(memory['counts'], 98.01)
    agent.new_half(AgentConfig(), memory)
    assert not memory['counts'].any()


@pytest.mark.parametrize('stack', [3, 5, 9, 80])
@pytest.mark.parametrize('style', ['pot', 'station', 'fold', 'switch'])
def test_legal_actions_through_short_stacks_caps_and_style_changes(stack, style, monkeypatch):
    import game as rules
    monkeypatch.setattr(rules, 'STARTING_STACK', stack)
    config = AgentConfig(starting_stack=stack, num_hands=24)
    memory = {}
    agent.new_half(config, memory)
    for hand in range(24):
        game = Game(make_deal('edge-legality', hand), hand % 2, hand)
        while not game.is_terminal:
            obs = game.observation(game.to_act)
            if game.to_act == hand % 2:
                action = agent.choose_action(obs, memory)
            else:
                active = ('pot' if hand % 2 else 'station') if style == 'switch' else style
                action = Action.CHECK_CALL
                if active == 'pot' and Action.RAISE_POT in obs.legal_actions:
                    action = Action.RAISE_POT
                elif active == 'fold' and obs.to_call:
                    action = Action.FOLD
            assert action in obs.legal_actions
            game.apply(action)
        agent.on_hand_end(game.hand_result(hand % 2), memory)
    assert memory['fallback_count'] == 0
