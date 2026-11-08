# jish_7 — optimization of a separate jish_4 copy

**284,000 test hands: 80,000 development, 192,000 fixed confirmation, and 12,000 official HTTP-judge hands.**

## Result

Equal-weight field change: **+0.0474 bb/duplicate deal**, 95% Student-t interval **[-0.0907, +0.1856]**.
Point change per match: +0.0104, seed-block interval [-0.0390, +0.0598].
Direct head-to-head against jish_4: +0.0355 bb/deal, interval [-0.1894, +0.2604].

Decision: The predeclared promotion checks did not all pass. Publish jish_7 as experimental and retain jish_4 as the default.

## What changed

- Bet-minus-check uncertainty is estimated using the same Monte Carlo samples, retaining their covariance. This is a decision heuristic, not a calibrated per-decision confidence guarantee.
- The adaptive margin permits clear, inexpensive value bets while requiring larger estimated gains when incremental payoff is uncertain.
- A public-board reference population estimates opponents’ calling-strength percentiles. Actual opponent-hand/runout simulations still exclude our private cards. Only the reference percentile distribution includes those cards as unknown to the opponent. This aims to avoid renormalizing away blockers; it is an approximation, not a solved opponent-belief model.
- jish_4’s preflop table, underlying numerical evaluator, learning, legal-action handling and server plumbing are preserved. Original jish_1–6 source/model/documents were verified unchanged.

Selected configuration: {'confidence': 1.0, 'adaptive': True, 'public_reference': True}.

## Paired confirmation by opponent

| Opponent | jish_4 bb/deal | jish_7 bb/deal | Paired change | 95% seed-block interval | Points change/match |
|---|---:|---:|---:|---|---:|
| jish_4 | +0.0000 | +0.0355 | +0.0355 | [-0.1894, +0.2604] | +0.0000 |
| main3 | +0.1678 | +0.2398 | +0.0720 | [-0.4015, +0.5455] | +0.0833 |
| quad2 | +2.8493 | +2.7923 | -0.0570 | [-0.3341, +0.2201] | +0.0000 |
| pocketedge2 | +1.7350 | +1.8977 | +0.1627 | [-0.0189, +0.3442] | +0.0000 |
| pokerbot2 | +1.8989 | +2.0297 | +0.1308 | [-0.3449, +0.6066] | +0.0000 |
| pot | +3.5182 | +3.5623 | +0.0442 | [-0.0793, +0.1676] | +0.0000 |
| pressure | -0.2535 | -0.2090 | +0.0445 | [-0.1088, +0.1978] | +0.0000 |
| trapper | +2.0730 | +2.0197 | -0.0533 | [-0.4060, +0.2994] | +0.0000 |

The candidate was selected from nine configurations on one development seed, then frozen before six fresh confirmation seeds. Within a block, candidate and baseline face the same eight opponents on identical deals, with fresh half-local state. Confidence intervals use six independent block averages, not individual hands as independent trials. Per-opponent intervals are exploratory and not adjusted for multiple comparisons. A constant observed point difference can yield a degenerate t interval; that is not proof of zero future score risk. These results describe this test population and seeds, not universal superiority.

## Official HTTP judge checks

| Opponent | Result for jish_7 | bb/duplicate deal | 95% judge interval |
|---|---|---:|---|
| jish_4 | CHOP | +0.0590 | [-0.3588, +0.4768] |
| pokerbot2 | AGENT1_WIN | +2.6870 | [+1.8935, +3.4805] |
| jish_6 research-spec | AGENT1_WIN | +1.2645 | [+0.5774, +1.9516] |
| PokerBot main3 / Active Guard | CHOP | +0.1910 | [-0.2748, +0.6568] |
| PocketEdge (2) | AGENT1_WIN | +2.1795 | [+1.4402, +2.9188] |
| Official calling station | AGENT1_WIN | +12.3795 | [+11.3394, +13.4196] |

Runtime: 0 errors; 0 forfeited halves; 0 exhausted time banks. Maximum charged half 1.488/8s. Maximum startup 1.777/15s. All 31 unit/interface/regression tests passed.

HTTP matches used the official 40BB game, 1,000 duplicate deals and fresh bot processes for each half. Two independent matches ran concurrently on local ports. CPU/memory limits were not isolated with Docker; a clean container build remains unverified. Direct confirmation timings are diagnostics, not substitutes for HTTP timing.

## Professional analysis

See RESEARCH_NOTES.md for the public Galfond–Kornuth heads-up PLO analysis and Polk–Negreanu hand analysis, their transfer to the hypotheses, and the limits of applying different variants. No professional hand-history dataset or inaccessible paid lesson was used.
