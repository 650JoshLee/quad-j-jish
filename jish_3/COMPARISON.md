# jish_3: measured comparison

**The new version is more extensively trained and calculates equity more precisely. These tests do not establish that it plays better than jish_2. Keep the previous version available.**

## Fresh head-to-head matches

| Opponent | Hands | Match wins / draws / losses | Mean bb per duplicate deal | 95% interval |
|---|---:|---:|---:|---:|
| jish_2 | 40,000 | 3 / 17 / 0 | +0.0083 | [-0.0746, +0.0913] |
| original jish_1 | 12,000 | 3 / 3 / 0 | +0.5947 | [+0.3975, +0.7918] |

Each duplicate deal combines both seats. The jish_2 interval includes zero, so the average chip gain is not statistically significant. All release seeds differ from development and tuning seeds.

## Matched practice field

Fourteen styles over two seeds: jish_3 26 wins, 2 draws, 0 losses. jish_2 scored 26 wins, 2 draws, 0 losses on the same deals.

| Opponent | jish_3 bb/deal | jish_2 bb/deal | Difference |
|---|---:|---:|---:|
| equity | +2.767 | +2.902 | -0.135 |
| half | +5.182 | +5.345 | -0.162 |
| loose | +3.644 | +3.735 | -0.091 |
| nit | +1.712 | +1.563 | +0.149 |
| pocketedge | +1.532 | +1.706 | -0.175 |
| polar | +2.711 | +2.800 | -0.089 |
| pot | +4.409 | +4.372 | +0.037 |
| pressure | -0.777 | -0.689 | -0.089 |
| quad | +1.438 | +1.582 | -0.143 |
| random | +9.885 | +10.151 | -0.266 |
| station | +11.822 | +11.967 | -0.144 |
| switcher | +2.188 | +2.022 | +0.165 |
| tight | +1.316 | +1.387 | -0.071 |
| trapper | +1.696 | +1.544 | +0.152 |

Equally weighted field difference: -0.062 bb/deal, 95% interval [-0.181, +0.058]. This also does not demonstrate a field-wide gain.

`quad` is the downloaded PokerBot-Team-quad-j-main submission (ShortDeckEquity). `pocketedge` is pocketedge-submission (2), PocketEdge v2. The other styles are inspectable practice policies in tools/arena.py, not professional or equilibrium solvers.

## Actual HTTP checks

Each half restarted both servers. The new bot beat original jish_1, both downloaded submissions, and a calling station; both additional matches against jish_2 were draws.

All 12 halves completed with zero errors, timeouts, forfeits, or skipped decisions for either bot. Maximum charged thinking time for jish_3: 3.958/8 seconds. Maximum new-bot startup: 2.169/15 seconds. These are local Mac timings, not tournament CPU measurements.

The downloaded PocketEdge macOS binary was blocked by system policy. Its supplied C source was compiled locally in an isolated test copy, and that compiled engine was used for the final comparisons. The downloaded original was not altered.

## Training and accuracy

Added 914,882,560 independent offline trials for 3,490 suit-equivalent starting-hand classes near decision thresholds. Those classes now have 327,680 trials each; the other classes retain their initial 65,536 trials. Both tables are included for reproduction.

For each sampled opponent holding, the main flop method checks all 253 legal turn/river runouts and the turn method checks all 22 legal river cards. On the river, the main method enumerates all 65,780 possible opponent holdings. A low-budget fallback uses sampling. Opponent range weights remain a heuristic, so exhaustive card calculation does not solve the betting game.

All 31 tests passed, including completeness, exact showdown comparisons, legal runouts, percentile ranks, budget fallback, half resets, and the original server/evaluator checks.

Development included threshold and learning-prior experiments. They did not justify replacing the conservative policy settings. Neither the rejected variants nor their scores are mixed into the release results.

The original jish_1 and jish_2 source/model files were fingerprinted before work and verified unchanged. Docker validation remains unavailable on this machine.
