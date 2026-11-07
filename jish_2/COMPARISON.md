# jish_2 comparison results

Against original jish_1: **6 wins, 4 draws, 0 losses** over 20,000 hands on ten untouched release seeds.

Mean advantage: **+0.596 bb per duplicate deal**; 95% confidence interval **[+0.442, +0.750]**. A duplicate deal combines both seats; this is not bb per individual hand.

Two additional full HTTP matches against the original were wins, at +0.680 and +0.724 bb per duplicate deal. Each half used fresh processes.

Across twelve practice opponent styles and two additional seeds, the new bot scored **22 wins, 2 draws, 0 losses**. The original scored the same match points. Both played the same deals.

| Opponent | jish_2 bb/deal | Original bb/deal | Difference |
|---|---:|---:|---:|
| equity | +3.550 | +3.341 | +0.209 |
| half | +5.803 | +5.803 | +0.000 |
| loose | +4.732 | +4.915 | -0.183 |
| nit | +1.747 | +1.744 | +0.003 |
| polar | +4.207 | +4.331 | -0.124 |
| pot | +5.212 | +5.212 | +0.000 |
| pressure | +0.373 | +0.373 | +0.000 |
| random | +10.384 | +10.462 | -0.078 |
| station | +11.800 | +11.747 | +0.053 |
| switcher | +2.472 | +2.519 | -0.046 |
| tight | +1.380 | +1.509 | -0.129 |
| trapper | +2.449 | +2.379 | +0.070 |

Across the equally weighted practice field, the mean chip difference was -0.019 bb/deal, with 95% interval [-0.136, +0.098]. This does **not** establish an overall field-wide chip advantage. The demonstrated gain is the direct matchup against the original, while broad practice performance stayed comparable.

The field includes random, calling, constant-raise, raw-equity, tight, slow-playing, polarized-bluffing, pressure, and changing-style policies. Inspect them in `tools/arena.py`. These are development opponents, not professional or equilibrium solvers.

All 12 final HTTP halves completed with zero errors, timeouts, forfeits, or skipped decisions. Maximum charged time: **0.642/8 seconds**. Maximum cold startup: **1.302/15 seconds**. Timings are local, not measurements on the tournament CPU.

All 24 tests passed. Tests cover evaluator correctness, the server, cautious learning, slow-play recognition, revealed-card-only updates, and half resets.

These are held-out results for the selected code. Earlier development experiments used separate seeds; rejected designs are excluded. Confidence intervals use the judge’s paired-deal normal approximation. Raw outcomes are in `validation/`.
