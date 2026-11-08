"""Rebuild the suit-invariant preflop table from legal, uniformly sampled deals.
Run from the repository root: python tools/train_preflop.py --samples 8192
Training is offline. The deployed bot only reads the resulting data file.
"""
import argparse
import itertools
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from numba import njit
os.environ['QUADJ_PRECOMPUTE'] = '1'
import agent


@njit
def canonical_map(hands, permutations):
    indexes = np.empty(len(hands), dtype=np.int32)
    converted = np.empty(5, dtype=np.int32)
    for i in range(len(hands)):
        best = 376992
        for perm in permutations:
            for j in range(5):
                card = hands[i, j]
                converted[j] = (card & ~3) | perm[card & 3]
            key = agent._index(converted)
            best = min(best, key)
        indexes[i] = best
    return indexes


@njit
def estimate(hole, samples, seed, table):
    state = np.uint64(seed)
    known = np.uint64(0)
    for c in hole:
        known |= np.uint64(1) << np.uint64(c)
    hr, hs = agent._pairs(hole)
    other = np.empty(5, dtype=np.int32)
    board = np.empty(5, dtype=np.int32)
    won = 0.0
    for _ in range(samples):
        used = known
        for j in range(10):
            while True:
                state, card = agent._random_card(state)
                bit = np.uint64(1) << np.uint64(card)
                if not used & bit:
                    break
            used |= bit
            if j < 5:
                other[j] = card
            else:
                board[j-5] = card
        a = agent._score_pairs(hr, hs, board, 5, table)
        b = agent._fast_score(other, board, table)
        won += 1.0 if a > b else 0.5 if a == b else 0.0
    return won / samples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--samples', type=int, default=8192)
    args = parser.parse_args()
    started = time.perf_counter()
    hands = np.array(list(itertools.combinations(range(36), 5)), dtype=np.int32)
    # Lexicographic enumeration is not combinadic order.
    by_index = np.empty_like(hands)
    for h in hands:
        by_index[agent._index(h)] = h
    perms = np.array(list(itertools.permutations(range(4))), dtype=np.int32)
    mapping = canonical_map(by_index, perms)
    unique = np.unique(mapping)
    print(f'{len(unique)} suit-invariant hands; {args.samples} simulations each', flush=True)
    values = np.zeros(376992, dtype=np.float32)
    for n, idx in enumerate(unique):
        values[idx] = estimate(by_index[idx], args.samples, np.uint64(413887 + int(idx) * 7919), agent._SCORE)
        if n % 1000 == 0:
            print(f'{n}/{len(unique)} ({time.perf_counter()-started:.1f}s)', flush=True)
    result = values[mapping]
    dest = Path(__file__).resolve().parents[1] / 'data'
    np.save(dest / 'preflop.npy', result, allow_pickle=False)
    (dest / 'preflop_metadata.json').write_text(json.dumps(dict(samples_per_class=args.samples, suit_classes=len(unique), total_hands=len(hands), seed_formula='413887 + canonical_index * 7919', min_equity=float(result.min()), max_equity=float(result.max()), mean_equity=float(result.mean()), elapsed_seconds=time.perf_counter()-started), indent=2)+'\n')
    print((dest / 'preflop_metadata.json').read_text(), flush=True)


if __name__ == '__main__':
    main()
