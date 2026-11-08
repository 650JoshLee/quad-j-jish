# jish_11: targeted improvements to jish_4

**Status: experimental. Default: jish_4.** All earlier jish_1–10 files were preserved.

## Changes

This version copies jish_4 and adds actual-raise-size response statistics, evaluates raises before folding a low-equity hand, and estimates one opponent re-raise followed by our fold/call response. The selected version enables all three features, blending 75% of the new continuation estimate with 25% of the original estimate. The evaluator and preflop model are unchanged. See BOT_NOTES.md for assumptions and limitations.

## Test design

Six development configurations (control, three single-feature variants, and two combined variants) faced 19 opponents on two seeds at 200 duplicate deals per match: **91,200 hands**. The better of the two combined variants was selected before fresh confirmation; single-feature versions were diagnostic. Keeping all three features active fulfills the requested experiment, not a claim that this is the strongest configuration found.

Four fresh seed blocks compared the frozen candidate and jish_4 against 22 opponents at 1,000 duplicate deals per match: **352,000 hands**. Three new strategy holdouts did not influence selection: size_folder folds to large raises, small_reraiser attacks small raises, and bluff_then_fold bets then folds to a raise. They are regression checks, excluded from the primary 19-opponent score. Primary scoring weights the nine real opponents and ten stress opponents equally as groups.

An additional 22 official HTTP matches covered **44,000 hands**. Total scored testing: **487,200 hands**. This is candidate-versus-field testing, not an all-pairs round robin.

All 31 rule/interface/strategy tests passed. New tests compare re-raise amounts directly with cloned official-game transitions, exercise cap handling and half resets, distinguish size-conditioned responses, check duplicate counting, and verify low-equity raises are considered against an extreme folder but rejected against a caller. Disabling new features matched jish_4 on 249 decisions over 100 parity-test hands, without fallbacks.

## Development diagnostics

| Configuration | Balanced bb/duplicate deal | Change versus control |
|---|---:|---:|
| control | +2.8846 | +0.0000 |
| sizes_only | +2.9653 | +0.0807 |
| bluffs_only | +2.8971 | +0.0125 |
| reraises_only | +2.8545 | -0.0301 |
| combined_light | +2.7428 | -0.1419 |
| combined_full | +2.8159 | -0.0688 |

Development scores are selection data, not independent evidence of improvement. Combining promising individual changes can hurt performance.

## Fresh paired comparison

- Balanced chip change: **-0.0557 bb/duplicate deal**, 95% seed-block interval [-0.12263019959961213, 0.0111538107107233].
- Balanced match-point change: **-0.0153**, 95% seed-block interval [-0.07006993807703725, 0.039514382521481706].
- Real-field chip change: -0.2205; stress-field change: +0.1090.

Intervals use Student t across four independent seed blocks (df=3); shared deals across opponents stay within each block. Four blocks provide limited precision. Per-opponent intervals are exploratory and not adjusted for multiple comparisons. Familiar test opponents are not newly unseen tournament entrants.

| Opponent | jish_11 bb/deal | jish_4 bb/deal | Change [95% interval] | jish_11 W/D/L |
|---|---:|---:|---|---|
| jish_4 | -0.206 | +0.000 | -0.206 [-0.445, +0.034] | 0/4/0 |
| main3 | -0.087 | +0.366 | -0.454 [-1.169, +0.262] | 0/4/0 |
| main4 | -1.721 | -1.412 | -0.309 [-1.273, +0.655] | 0/0/4 |
| quad2 | +2.779 | +2.719 | +0.060 [-0.430, +0.549] | 4/0/0 |
| pocketedge2 | +1.408 | +1.620 | -0.212 [-0.425, +0.002] | 4/0/0 |
| pokerbot2 | +2.127 | +1.901 | +0.225 [-0.513, +0.963] | 4/0/0 |
| jish_2 | +0.081 | +0.137 | -0.056 [-0.348, +0.236] | 0/4/0 |
| jish_6 | +0.849 | +1.295 | -0.447 [-0.991, +0.098] | 3/1/0 |
| pot | +4.816 | +4.834 | -0.018 [-0.137, +0.100] | 4/0/0 |
| station | +11.654 | +11.662 | -0.008 [-0.034, +0.019] | 4/0/0 |
| nit | +1.689 | +1.760 | -0.071 [-0.267, +0.126] | 4/0/0 |
| pressure | +0.422 | -0.047 | +0.469 [-0.218, +1.156] | 1/3/0 |
| trapper | +2.663 | +2.099 | +0.564 [+0.351, +0.776] | 4/0/0 |
| polar | +3.953 | +3.669 | +0.284 [+0.016, +0.552] | 4/0/0 |
| switcher | +3.065 | +2.742 | +0.323 [-0.010, +0.656] | 4/0/0 |
| random | +9.911 | +9.724 | +0.187 [-0.961, +1.336] | 4/0/0 |
| delayed_pot | +11.631 | +12.173 | -0.542 [-1.036, -0.047] | 4/0/0 |
| station_maniac | +8.947 | +9.045 | -0.098 [-0.242, +0.046] | 4/0/0 |
| jish_8 | -0.337 | +0.250 | -0.587 [-1.428, +0.254] | 0/3/1 |
| size_folder (held out) | +5.525 | +0.141 | +5.383 [+4.946, +5.821] | 4/0/0 |
| small_reraiser (held out) | +11.638 | +11.635 | +0.004 [-0.292, +0.300] | 4/0/0 |
| bluff_then_fold (held out) | +8.064 | +6.297 | +1.767 [+1.690, +1.845] | 4/0/0 |

## Official HTTP results

Fresh process per half, 1,000 duplicate deals per match, official 95% verdict. Values are jish_11’s results.

| Opponent | bb/duplicate deal | 95% interval | Result |
|---|---:|---|---|
| bluff_then_fold | +8.444 | [+8.175, +8.714] | AGENT1_WIN |
| delayed_pot | +11.182 | [+9.640, +12.725] | AGENT1_WIN |
| jish_2 | -0.703 | [-1.204, -0.202] | AGENT2_WIN |
| jish_4 | -0.362 | [-0.847, +0.123] | CHOP |
| jish_6 | +0.789 | [+0.178, +1.401] | AGENT1_WIN |
| jish_8 | -0.785 | [-1.317, -0.253] | AGENT2_WIN |
| main3 | -0.372 | [-0.863, +0.119] | CHOP |
| main4 | -2.202 | [-3.048, -1.356] | AGENT2_WIN |
| nit | +1.812 | [+1.226, +2.398] | AGENT1_WIN |
| pocketedge2 | +2.080 | [+1.341, +2.820] | AGENT1_WIN |
| pokerbot2 | +1.831 | [+1.076, +2.586] | AGENT1_WIN |
| polar | +3.873 | [+2.859, +4.888] | AGENT1_WIN |
| pot | +3.654 | [+1.886, +5.421] | AGENT1_WIN |
| pressure | +0.147 | [-0.829, +1.124] | CHOP |
| quad2 | +2.534 | [+1.723, +3.344] | AGENT1_WIN |
| random | +7.638 | [+6.135, +9.142] | AGENT1_WIN |
| size_folder | +5.981 | [+5.527, +6.434] | AGENT1_WIN |
| small_reraiser | +12.450 | [+11.386, +13.513] | AGENT1_WIN |
| station | +12.415 | [+11.350, +13.479] | AGENT1_WIN |
| station_maniac | +9.377 | [+7.978, +10.777] | AGENT1_WIN |
| switcher | +2.244 | [+0.898, +3.591] | AGENT1_WIN |
| trapper | +2.441 | [+1.630, +3.252] | AGENT1_WIN |

HTTP outcomes: {'CHOP': 3, 'AGENT2_WIN': 3, 'AGENT1_WIN': 16}. Errors: 0; forfeits: 0; exhausted banks: 0. Maximum charged half-bank: 1.099/8 seconds. Maximum startup: 1.316/15 seconds. Direct confirmation fallbacks: 0.

## Promotion decision

Before confirmation, promotion required positive chip and point intervals, nonnegative real/stress mean changes, no clearly material opponent regression (upper interval below -0.25 bb/deal), no clear direct loss to jish_4 or jish_8, and clean runtime tests.

Checks: `{'positive_chip_interval': False, 'positive_point_interval': False, 'nonnegative_real_mean': False, 'nonnegative_stress_mean': True, 'no_material_regression': True, 'no_clear_direct_loss': False, 'runtime_clean': True}`.
Material opponent regressions detected: `[]`. Clear direct losses (fresh block interval or official HTTP interval): `['jish_8']`.
Default decision: **jish_4**.

## Practical limitations

The extra branch still approximates opponent ranges and stops after one re-raise; it is not a full-street solver. Future-street betting, draw-aware range likelihoods, recency weighting and full position/board-dependent response learning remain unimplemented. The equal mixture of opponent raise sizes and the blend weight are heuristics. Runtime depends partly on adaptive sample counts and can vary across machines.

Results apply to the sampled field and seeds, not every possible opponent. Docker is unavailable locally: no clean container build or isolated tournament CPU/memory certification was performed. Existing local official-judge checks are not a hardware-independent guarantee.
