# jish_10: independent Slumbot-inspired experiment

**Experimental only. Keep jish_4 as the default.** The simplified solver does not demonstrate broad improvement. Existing jish_1–9 files were preserved.

## Approach

New implementation from the official starter: sampled legal Omaha equity, eight private strength buckets, and current-street positive-regret matching. No earlier strategy code/data or Slumbot policy was reused. See the bot’s RESEARCH_NOTES.md for primary sources and approximation limits.

## Tests and selection

Three finite configurations were compared over two development seeds against 19 opponents (45,600 hands). The base configuration had the highest equally weighted real/stress score and was frozen before fresh confirmation. Two new confirmation seeds tested both jish_10 and jish_4 against the same 19 opponents (152,000 hands). The official HTTP judge then ran 19 additional 2,000-hand matches (38,000 hands): **235,600 total test hands**. These are candidate-vs-field comparisons, not an all-pairs tournament.

Numerical checks covered every 376,992 five-card combination, 500 Omaha hands, 33,847 betting-tree states, and a Kuhn poker equilibrium check. Kuhn value -0.0555606 matches the known -1/18; best-response gap 0.002284 at 10,000 iterations. This proves neither full-PLO convergence nor strength. All 12 official interface tests passed.

## Paired fresh comparison

Each field gives equal weight to real and stress opponents. The intervals below use Student t across two seed blocks (df=1), retaining cross-opponent correlation within a block. Only two blocks give very limited precision. Development results are excluded.

- Balanced chip change: -2.6238 bb/duplicate deal; 95% seed-block interval [-3.713957887433601, -1.5337143347886217].
- Balanced match-point change: -0.3653; 95% seed-block interval [-0.5241053369777776, -0.20645021857777804].

| Opponent | jish_10 bb/deal | jish_4 bb/deal | Change | jish_10 W/D/L |
|---|---:|---:|---:|---|
| jish_4 | -2.077 | +0.000 | -2.077 | 0/0/2 |
| main3 | -2.220 | +0.165 | -2.385 | 0/0/2 |
| main4 | -1.164 | -0.871 | -0.293 | 0/0/2 |
| quad2 | +0.050 | +2.655 | -2.605 | 0/2/0 |
| pocketedge2 | -0.701 | +2.380 | -3.080 | 0/1/1 |
| pokerbot2 | -0.404 | +2.357 | -2.761 | 0/2/0 |
| jish_2 | -2.341 | -0.085 | -2.256 | 0/0/2 |
| jish_6 | -1.873 | +1.321 | -3.193 | 0/0/2 |
| pot | +2.582 | +4.499 | -1.918 | 2/0/0 |
| station | +2.639 | +11.333 | -8.694 | 2/0/0 |
| nit | +0.277 | +1.766 | -1.489 | 0/2/0 |
| pressure | -1.752 | -0.279 | -1.474 | 0/0/2 |
| trapper | +0.874 | +2.084 | -1.210 | 2/0/0 |
| polar | +0.462 | +3.387 | -2.925 | 0/2/0 |
| switcher | -0.021 | +1.350 | -1.370 | 0/2/0 |
| random | +6.838 | +8.828 | -1.989 | 2/0/0 |
| delayed_pot | +7.613 | +10.653 | -3.040 | 2/0/0 |
| station_maniac | +2.961 | +8.389 | -5.428 | 2/0/0 |
| jish_8 | -2.071 | -0.077 | -1.995 | 0/0/2 |

## Official HTTP results

Fresh process per half, 1,000 duplicate deals per match, official 95% verdict. Values are jish_10’s results.

| Opponent | bb/duplicate deal | 95% interval | Result |
|---|---:|---|---|
| delayed_pot | +8.678 | [+7.173, +10.182] | AGENT1_WIN |
| jish_2 | -2.178 | [-3.148, -1.207] | AGENT2_WIN |
| jish_4 | -1.653 | [-2.599, -0.707] | AGENT2_WIN |
| jish_6 | -1.401 | [-2.169, -0.634] | AGENT2_WIN |
| jish_8 | -1.510 | [-2.443, -0.577] | AGENT2_WIN |
| main3 | -1.817 | [-2.783, -0.852] | AGENT2_WIN |
| main4 | -0.430 | [-1.158, +0.298] | CHOP |
| nit | +0.138 | [-0.307, +0.582] | CHOP |
| pocketedge2 | +0.073 | [-0.436, +0.582] | CHOP |
| pokerbot2 | -0.485 | [-1.023, +0.052] | CHOP |
| polar | +0.807 | [+0.016, +1.599] | AGENT1_WIN |
| pot | +2.744 | [+1.663, +3.824] | AGENT1_WIN |
| pressure | -3.215 | [-4.411, -2.019] | AGENT2_WIN |
| quad2 | -0.280 | [-0.857, +0.297] | CHOP |
| random | +6.431 | [+4.858, +8.003] | AGENT1_WIN |
| station | +3.612 | [+2.968, +4.257] | AGENT1_WIN |
| station_maniac | +3.101 | [+1.841, +4.361] | AGENT1_WIN |
| switcher | -0.574 | [-1.679, +0.532] | CHOP |
| trapper | +1.119 | [+0.475, +1.763] | AGENT1_WIN |

HTTP outcomes: {'AGENT2_WIN': 6, 'CHOP': 6, 'AGENT1_WIN': 7}. Errors: 0; forfeits: 0; exhausted banks: 0. Maximum jish_10 charged half-bank: 0.852/8 seconds. Maximum startup: 1.777/15 seconds.

## Decision and limitations

Promotion required broad chip and point improvement without significant direct losses to jish_4/jish_8 or material opponent regressions. The evidence fails this gate, so the new version is published as experimental and the root default remains jish_4. A current-street equilibrium of an approximate game is not a full-game PLO solution. The missing future-street betting model, rough private-hand buckets and heuristic ranges are plausible causes of weakness, not experimentally isolated explanations. More iterations alone do not repair the abstraction.

These are local results, not proof of tournament ranking. Official HTTP timing passed on this machine only; Docker is not installed, so a clean container build and exact one-CPU tournament hardware have not been certified. Bundled numerical dependencies must be available in that environment. No live Slumbot match or hidden policy extraction was performed.
