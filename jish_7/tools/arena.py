"""Duplicate matches against diverse policies and an optional reference bot.
The direct engine checks legality and counts outcomes, but is not an HTTP timing test.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import numpy as np
import agent
from game import Action, AgentConfig, Game, make_deal


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Practice:
    """Deliberately different imperfect opponents, not claims of optimal play."""
    def __init__(self, style):
        self.style = style

    def new_half(self, config, memory):
        memory.clear()
        memory.update(rng=random.Random(0), cache=None)

    def on_hand_end(self, result, memory):
        pass

    def choose_action(self, obs, memory):
        style = self.style
        rng = memory['rng']
        legal = obs.legal_actions
        if style == 'random':
            return rng.choice(legal)
        if style == 'station':
            return Action.CHECK_CALL
        if style in ('pot', 'half'):
            choice = Action.RAISE_POT if style == 'pot' else Action.RAISE_HALF
            return choice if choice in legal else Action.CHECK_CALL
        if style == 'fold':
            return Action.FOLD if obs.to_call else Action.CHECK_CALL
        if not obs.board:
            eq = float(agent._PREFLOP[agent._index(np.array(obs.hole_cards, dtype=np.int32))])
        else:
            key = (obs.hand_index, obs.hole_cards, obs.board)
            if memory['cache'] is None or memory['cache'][0] != key:
                _, _, result = agent._sample(np.array(obs.hole_cards, dtype=np.int32), np.array(obs.board, dtype=np.int32), 384, 3, np.uint64(rng.getrandbits(63) | 1), agent._SCORE, agent._PREFLOP)
                memory['cache'] = (key, float(result.mean()))
            eq = memory['cache'][1]
        free = obs.to_call == 0
        can_raise = Action.RAISE_POT in legal
        pre = not obs.board
        odds = obs.to_call / max(1, obs.pot + obs.to_call)
        if style in ('tight', 'equity', 'loose'):
            threshold = {'tight': .57, 'equity': .53, 'loose': .49}[style] if pre else {'tight': .73, 'equity': .62, 'loose': .54}[style]
            premium = {'tight': .16, 'equity': .06, 'loose': 0.}[style] if obs.opp_stack else 0.
            if can_raise and eq > threshold:
                return Action.RAISE_POT
            return Action.CHECK_CALL if free or eq > odds + premium else Action.FOLD
        if style == 'nit':
            if can_raise and eq > (.60 if pre else .85):
                return Action.RAISE_POT
            return Action.CHECK_CALL if free or eq > max(odds + .1, .44 if pre else .56) else Action.FOLD
        if style == 'trapper':
            if can_raise and eq > (.56 if pre else .74) and (not free or rng.random() < .20):
                return Action.RAISE_POT
            if can_raise and free and .43 < eq < .58 and rng.random() < .22:
                return Action.RAISE_HALF
            return Action.CHECK_CALL if free or eq > odds + .055 else Action.FOLD
        if style == 'polar':
            value = eq > (.55 if pre else .74)
            bluff = (eq < (.44 if pre else .36) and rng.random() < (.16 if pre else .24))
            if can_raise and (value or bluff):
                return Action.RAISE_POT
            return Action.CHECK_CALL if free or eq > odds + .08 else Action.FOLD
        if style == 'pressure':
            # Attack checks and small pots; continue more carefully versus raises.
            prior_raises = sum(a.is_me and a.action in (Action.RAISE_HALF, Action.RAISE_POT) and a.street == obs.street for a in obs.action_history)
            if can_raise and ((free and rng.random() < .85) or eq > (.54 if pre else .68)):
                return Action.RAISE_HALF if free else Action.RAISE_POT
            return Action.CHECK_CALL if free or eq > odds + (.18 if prior_raises else .04) else Action.FOLD
        if style == 'switcher':
            # Change style during the half to challenge stale opponent estimates.
            old = self.style
            self.style = 'pot' if (obs.hand_index // 100) % 2 == 0 else 'tight'
            try:
                return self.choose_action(obs, memory)
            finally:
                self.style = old
        raise ValueError(style)


def match(bot, rival, deals, seed):
    nets = np.zeros(deals)
    counts = [0, 0, 0]
    times, fallbacks, charged = [], [], []
    start = time.perf_counter()
    for seat in (0, 1):
        ours, theirs = {}, {}
        # Always reset at tournament half length; larger tests are separate seeds.
        config = AgentConfig(num_hands=deals)
        bot.new_half(config, ours)
        rival.new_half(config, theirs)
        cpu = charge = 0.
        for hand in range(deals):
            game = Game(make_deal(seed, hand), hand % 2, hand)
            while not game.is_terminal:
                actor = game.to_act
                obs = game.observation(actor)
                if actor == seat:
                    t = time.perf_counter()
                    action = bot.choose_action(obs, ours)
                    elapsed = time.perf_counter() - t
                    cpu += elapsed
                    charge += max(0., elapsed - .001)
                    if elapsed >= 1:
                        raise RuntimeError('Decision exceeded one second')
                else:
                    action = rival.choose_action(obs, theirs)
                assert action in obs.legal_actions, (action, obs)
                game.apply(action)
            result = game.hand_result(seat)
            nets[hand] += result.my_net / config.big_blind
            counts[0 if result.my_net > 0 else 1 if result.my_net < 0 else 2] += 1
            bot.on_hand_end(result, ours)
            rival.on_hand_end(game.hand_result(1-seat), theirs)
        times.append(cpu)
        charged.append(charge)
        fallbacks.append(ours.get('fallback_count', 0))
    mean = float(nets.mean())
    margin = 1.96 * float(nets.std(ddof=1)) / np.sqrt(deals)
    return dict(seed=seed, deals=deals, hands=2*deals, mean_bb=mean,
                ci95=[mean-margin, mean+margin], verdict='WIN' if mean>margin else 'LOSS' if mean < -margin else 'CHOP',
                hands_won=counts[0], hands_lost=counts[1], ties=counts[2],
                compute_seconds=times, direct_charged_seconds=charged, fallbacks=fallbacks,
                elapsed_seconds=time.perf_counter()-start, paired_bb=nets.tolist())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--bot', type=Path)
    parser.add_argument('--opponents', nargs='+', default=['original','random','station','pot','half','tight','equity','loose','nit','trapper','polar','pressure','switcher'])
    parser.add_argument('--seeds', nargs='+', default=['development-new-1'])
    parser.add_argument('--deals', type=int, default=1000)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    bot = load(args.bot.resolve(), 'candidate') if args.bot else agent
    ref = load(args.reference.resolve(), 'reference') if args.reference else None
    if 'original' in args.opponents and ref is None:
        parser.error('--reference is required when playing original')
    results = []
    for seed in args.seeds:
        for style in args.opponents:
            result = match(bot, ref if style == 'original' else Practice(style), args.deals, seed)
            result['opponent'] = style
            results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k != 'paired_bb'}), flush=True)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(results, indent=2)+'\n')


if __name__ == '__main__':
    main()
