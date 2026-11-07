"""Duplicate strategy matches; use judge_engine.py for HTTP time-bank checks."""
import argparse
import json
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import agent
from game import Action, AgentConfig, Game, make_deal


def opponent(obs, memory, style):
    legal = obs.legal_actions
    if style == 'random':
        return memory['rng'].choice(legal)
    if style == 'station':
        return Action.CHECK_CALL
    if style in ('pot', 'half'):
        a = Action.RAISE_POT if style == 'pot' else Action.RAISE_HALF
        return a if a in legal else Action.CHECK_CALL
    if style == 'fold':
        return Action.CHECK_CALL if obs.to_call == 0 else Action.FOLD
    if style == 'mirror':
        return agent.choose_action(obs, memory)
    # Independent raw-equity policies with three aggression levels.
    if not obs.board:
        equity = float(agent._PREFLOP[agent._index(np.asarray(obs.hole_cards, dtype=np.int32))])
    else:
        key = (obs.hand_index, obs.board)
        if memory.get('key') != key:
            _, _, results = agent._sample(np.asarray(obs.hole_cards, dtype=np.int32), np.asarray(obs.board, dtype=np.int32), 384, 2, np.uint64(memory['rng'].getrandbits(63) | 1), agent._SCORE, agent._PREFLOP)
            memory['equity'], memory['key'] = float(results.mean()), key
        equity = memory['equity']
    cutoff = {'tight': 0.73, 'equity': 0.62, 'loose': 0.54}[style]
    if not obs.board:
        cutoff = {'tight': 0.57, 'equity': 0.53, 'loose': 0.49}[style]
    if equity > cutoff and Action.RAISE_POT in legal:
        return Action.RAISE_POT
    price = obs.to_call / (obs.pot + obs.to_call)
    premium = {'tight': 0.16, 'equity': 0.06, 'loose': 0.0}[style] if obs.opp_stack else 0
    if not obs.to_call or equity > price + premium:
        return Action.CHECK_CALL
    return Action.FOLD


def match(style, deals, seed):
    net = np.zeros(deals)
    times, fallbacks = [], []
    won = lost = tied = 0
    started = time.perf_counter()
    for our_seat in range(2):
        memory, other = {}, {}
        agent.new_half(AgentConfig(num_hands=deals), memory)
        agent.new_half(AgentConfig(num_hands=deals), other)
        for hand in range(deals):
            game = Game(make_deal(seed, hand), hand % 2, hand)
            while not game.is_terminal:
                seat = game.to_act
                obs = game.observation(seat)
                action = agent.choose_action(obs, memory) if seat == our_seat else opponent(obs, other, style)
                if action not in obs.legal_actions:
                    raise AssertionError((action, obs))
                game.apply(action)
            result = game.hand_result(our_seat)
            net[hand] += result.my_net / 2
            won += result.my_net > 0
            lost += result.my_net < 0
            tied += result.my_net == 0
            agent.on_hand_end(result, memory)
            if style == 'mirror':
                agent.on_hand_end(game.hand_result(1-our_seat), other)
        times.append(memory['compute_seconds'])
        fallbacks.append(memory['fallback_count'])
    mean = float(net.mean())
    error = 1.96 * float(net.std(ddof=1)) / deals ** 0.5
    return dict(opponent=style, deals=deals, hands=deals*2, hands_won=won, hands_lost=lost, hands_tied=tied, seed=seed, bb_per_duplicate=mean, ci95=[mean-error,mean+error], verdict='WIN' if mean-error > 0 else 'LOSS' if mean+error < 0 else 'CHOP', compute_seconds=times, fallbacks=fallbacks, elapsed_seconds=time.perf_counter()-started)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--opponents', nargs='+', default=['random', 'station', 'pot', 'half', 'tight', 'equity', 'loose'])
    parser.add_argument('--deals', type=int, default=1000)
    parser.add_argument('--seed', default='development-1')
    parser.add_argument('--json')
    args = parser.parse_args()
    results = []
    for style in args.opponents:
        result = match(style, args.deals, args.seed)
        results.append(result)
        print(json.dumps(result), flush=True)
        if args.json:
            Path(args.json).write_text(json.dumps(results, indent=2)+'\n')


if __name__ == '__main__':
    main()
