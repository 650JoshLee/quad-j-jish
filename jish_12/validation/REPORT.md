# jish_12: final conservative adjustment audit

**Status: experimental. Default: jish_4.** All previous jish_1–11 files were preserved.

## Changes

This version copies jish_4 and records opponent responses by street, actual raise size and whether our bet faced a bet. It changes the response estimate only after sufficient relevant observations and a meaningful estimated departure. Low-equity bluff raises are considered only when a conservative observed-fold estimate clears a pure-bluff break-even check plus the original betting margin. Estimates remain shrunk toward the old model. The selected version enables both features with 16 minimum relevant observations. The evaluator, model, preflop policy and official server remain unchanged. The unsuccessful jish_11 re-raise branch is not used.

The interval-based gates are heuristics, not guarantees of future profit. See AUDIT.md and BOT_NOTES.md for remaining limitations.

## Test design

Six development configurations (control, contextual learning with 16/32 observations, bluff-only with 32, and two combined variants) faced 19 opponents on two seeds at 200 duplicate deals per match: **91,200 hands**. The highest-scoring new configuration was frozen before confirmation.

Four fresh seed blocks compared the frozen candidate and jish_4 against **32 opponents**, 1,000 duplicate deals per match: **512,000 hands**. This includes every earlier jish, five external real bots, ten existing stress styles, three structured size/bluff styles and three newly added deception/switching styles. The primary score uses the original 19-opponent field with equal weights for nine real bots and ten stress bots. The remaining thirteen are regression checks, excluded from the primary score. They did not select the candidate; most are familiar strategies, not all novel holdouts.

An additional 32 official HTTP matches covered **64,000 hands**. Total scored testing: **667,200 hands**. This is candidate-versus-field testing, not another all-pairs round robin.

All 38 local rule/interface/strategy tests passed. These include exhaustive five-card lookup validation, independent Omaha checks, legal sampling, memory reset, evidence/context separation, terminal accounting, cap handling and bluff-gate regressions. Disabling the new features matched jish_4 on 271 decisions across 100 hands without fallback. Python 3.12 Linux pinned dependency wheels also resolved. The public GitHub CI result below separately reports Python 3.12 tests and official Docker build/smoke checks for jish_4 and jish_12.

## Development diagnostics

| Configuration | Balanced bb/duplicate deal | Change versus control |
|---|---:|---:|---:|
| control | +3.5324 | +0.0000 |
| context_16 | +3.5782 | +0.0458 |
| context_32 | +3.5763 | +0.0439 |
| bluff_32 | +3.5929 | +0.0606 |
| combined_16 | +3.6222 | +0.0898 |
| combined_32 | +3.5922 | +0.0599 |

Development scores are selection data, not independent evidence of improvement. Combining promising individual changes can hurt performance.

## Fresh paired comparison

- Balanced chip change: **-0.0668 bb/duplicate deal**, 95% seed-block interval [-0.19483726502529142, 0.06129143169195807].
- Balanced match-point change: **-0.0069**, 95% seed-block interval [-0.029044766006944445, 0.015155877118055557].
- Real-field chip change: -0.1190; stress-field change: -0.0146.

Intervals use Student t across four independent seed blocks (df=3); shared deals across opponents stay within each block. Four blocks provide limited precision. Per-opponent intervals are exploratory and not adjusted for multiple comparisons. Familiar test opponents are not newly unseen tournament entrants.

| Opponent | jish_12 bb/deal | jish_4 bb/deal | Change [95% interval] | jish_12 W/D/L |
|---|---:|---:|---|---|
| jish_4 | +0.027 | +0.000 | +0.027 [-0.167, +0.221] | 0/4/0 |
| main3 | +0.164 | +0.211 | -0.047 [-0.250, +0.155] | 1/3/0 |
| main4 | -1.062 | -1.069 | +0.007 [-0.070, +0.083] | 0/0/4 |
| quad2 | +2.593 | +2.741 | -0.148 [-0.527, +0.230] | 4/0/0 |
| pocketedge2 | +1.984 | +2.019 | -0.036 [-0.117, +0.046] | 4/0/0 |
| pokerbot2 | +1.604 | +2.168 | -0.564 [-1.446, +0.317] | 4/0/0 |
| jish_2 | +0.164 | +0.263 | -0.099 [-0.294, +0.096] | 0/4/0 |
| jish_6 | +1.449 | +1.554 | -0.104 [-0.404, +0.195] | 4/0/0 |
| pot | +4.346 | +4.346 | +0.000 [+0.000, +0.000] | 4/0/0 |
| station | +12.027 | +12.029 | -0.002 [-0.031, +0.027] | 4/0/0 |
| nit | +1.639 | +1.639 | +0.000 [+0.000, +0.000] | 4/0/0 |
| pressure | -0.497 | -0.307 | -0.191 [-0.699, +0.318] | 0/3/1 |
| trapper | +1.578 | +1.478 | +0.100 [-0.445, +0.646] | 4/0/0 |
| polar | +3.147 | +3.288 | -0.142 [-0.915, +0.632] | 4/0/0 |
| switcher | +2.003 | +1.921 | +0.082 [-0.094, +0.258] | 4/0/0 |
| random | +9.632 | +9.632 | +0.000 [+0.000, +0.000] | 4/0/0 |
| delayed_pot | +12.065 | +12.065 | +0.000 [+0.000, +0.000] | 4/0/0 |
| station_maniac | +9.213 | +9.207 | +0.006 [-0.013, +0.025] | 4/0/0 |
| jish_1 (held out) | +0.621 | +0.712 | -0.091 [-0.411, +0.230] | 3/1/0 |
| jish_3 (held out) | +0.076 | +0.133 | -0.057 [-0.637, +0.524] | 1/2/1 |
| jish_5 (held out) | +0.888 | +0.980 | -0.092 [-0.566, +0.382] | 1/3/0 |
| jish_7 (held out) | +0.025 | -0.105 | +0.130 [-0.075, +0.336] | 0/4/0 |
| jish_8 | +0.108 | +0.213 | -0.105 [-0.256, +0.046] | 0/4/0 |
| jish_9 (held out) | +0.027 | +0.000 | +0.027 [-0.167, +0.221] | 0/4/0 |
| jish_10 (held out) | +1.832 | +1.810 | +0.022 [-0.679, +0.723] | 4/0/0 |
| jish_11 (held out) | -0.006 | -0.172 | +0.166 [-0.343, +0.675] | 1/3/0 |
| size_folder (held out) | +5.756 | -0.057 | +5.813 [+5.090, +6.536] | 4/0/0 |
| small_reraiser (held out) | +11.966 | +11.979 | -0.013 [-0.047, +0.022] | 4/0/0 |
| bluff_then_fold (held out) | +7.938 | +6.608 | +1.330 [+1.155, +1.505] | 4/0/0 |
| fast_switch (held out) | +8.988 | +8.988 | +0.000 [+0.000, +0.000] | 4/0/0 |
| late_trap (held out) | +8.756 | +8.986 | -0.230 [-0.315, -0.145] | 4/0/0 |
| alternating_sizes (held out) | +6.426 | +5.776 | +0.650 [-0.250, +1.551] | 4/0/0 |

## Official HTTP results

Fresh process per half, 1,000 duplicate deals per match, official 95% verdict. Values are jish_12’s results.

| Opponent | bb/duplicate deal | 95% interval | Result |
|---|---:|---|---|
| alternating_sizes | +6.124 | [+4.577, +7.671] | AGENT1_WIN |
| bluff_then_fold | +7.720 | [+7.463, +7.977] | AGENT1_WIN |
| delayed_pot | +11.552 | [+10.048, +13.056] | AGENT1_WIN |
| fast_switch | +9.508 | [+8.077, +10.939] | AGENT1_WIN |
| jish_1 | +0.799 | [+0.294, +1.304] | AGENT1_WIN |
| jish_10 | +2.564 | [+1.603, +3.526] | AGENT1_WIN |
| jish_11 | +0.089 | [-0.421, +0.599] | CHOP |
| jish_2 | -0.091 | [-0.483, +0.301] | CHOP |
| jish_3 | -0.217 | [-0.660, +0.226] | CHOP |
| jish_4 | -0.197 | [-0.524, +0.130] | CHOP |
| jish_5 | +0.684 | [-0.186, +1.554] | CHOP |
| jish_6 | +1.552 | [+0.812, +2.291] | AGENT1_WIN |
| jish_7 | -0.460 | [-0.944, +0.024] | CHOP |
| jish_8 | -0.558 | [-1.027, -0.089] | AGENT2_WIN |
| jish_9 | -0.197 | [-0.524, +0.130] | CHOP |
| late_trap | +8.516 | [+7.149, +9.883] | AGENT1_WIN |
| main3 | +0.054 | [-0.408, +0.516] | CHOP |
| main4 | -1.456 | [-2.235, -0.677] | AGENT2_WIN |
| nit | +1.379 | [+0.890, +1.867] | AGENT1_WIN |
| pocketedge2 | +2.088 | [+1.368, +2.808] | AGENT1_WIN |
| pokerbot2 | +1.372 | [+0.618, +2.126] | AGENT1_WIN |
| polar | +3.825 | [+2.818, +4.832] | AGENT1_WIN |
| pot | +4.973 | [+3.221, +6.726] | AGENT1_WIN |
| pressure | -0.108 | [-1.019, +0.802] | CHOP |
| quad2 | +3.107 | [+2.290, +3.923] | AGENT1_WIN |
| random | +9.636 | [+8.152, +11.119] | AGENT1_WIN |
| size_folder | +5.980 | [+5.475, +6.485] | AGENT1_WIN |
| small_reraiser | +12.690 | [+11.650, +13.730] | AGENT1_WIN |
| station | +12.825 | [+11.781, +13.869] | AGENT1_WIN |
| station_maniac | +9.021 | [+7.593, +10.449] | AGENT1_WIN |
| switcher | +1.484 | [+0.119, +2.849] | AGENT1_WIN |
| trapper | +3.394 | [+2.553, +4.235] | AGENT1_WIN |

HTTP outcomes: {'CHOP': 9, 'AGENT2_WIN': 2, 'AGENT1_WIN': 21}. Errors: 0; forfeits: 0; exhausted banks: 0. Maximum charged half-bank: 1.183/8 seconds. Maximum startup: 1.734/15 seconds. Direct confirmation fallbacks: 0.

## Promotion decision

Before confirmation, promotion required positive chip and point intervals, nonnegative real/stress mean changes, no clearly material opponent regression (upper interval below -0.25 bb/deal), no clear direct loss to jish_4/jish_7/jish_8/jish_9, clean runtime tests and a successful container check.

Checks: `{'positive_chip_interval': False, 'positive_point_interval': False, 'nonnegative_real_mean': False, 'nonnegative_stress_mean': False, 'no_material_regression': True, 'no_clear_direct_loss': False, 'runtime_clean': True, 'container_checks_passed': True}`.
Material opponent regressions detected: `[]`. Clear direct losses (fresh block interval or official HTTP interval): `['jish_8']`.
Default decision: **jish_4**.

## Container verification

Official CI: [success](https://github.com/650JoshLee/quad-j-jish/actions/runs/42458430682) for frozen source commit `bc6522a7374e524c7037feb9b9cefa3e7aa6d124`. The workflow checks both jish_4 and jish_12 on Python 3.12, builds the official base and agent images, checks added image size, then runs the official smoke test with one CPU, 4 GB RAM, no network, read-only root, /tmp capped at 512 MB, and no extra privileges. Check container-jobs.json for per-step outcomes. A passing smoke test is not a full container tournament and does not guarantee every deployment environment.

## Practical limitations

This remains a heuristic equity bot. Full multi-street planning, richer draw/blocker range models, recency weighting and an equilibrium strategy are not implemented. Current evidence gates can be misled by changing or deceptive opponents despite the targeted tests. Confidence calculations on adaptive, partially pooled observations are heuristic. Exact runtime depends on hardware and adaptive sample counts.

The saved audit lists what was tested and what remains approximate. No finite test suite can prove that every possible weakness has been removed. No further strategy selection used the four confirmation blocks. Public GitHub standard runners were used only for free validation; no paid resources or live online poker were used.
