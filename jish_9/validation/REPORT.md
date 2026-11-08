# jish_9 — broad-field optimization of jish_4

**920,000 test hands:** 308,000 development, 576,000 frozen confirmation, and 36,000 official HTTP judge hands.

**Retain jish_4 as default. Publish jish_9 as experimental: not all promotion criteria passed.**

The balanced chip-profit improvement passes its confidence checks, including with main4 excluded. Promotion is blocked by an inconclusive real-field tournament-point change and a material regression against delayed_pot: -0.4235 bb/duplicate deal, 95% interval [-0.5633, -0.2837]. Both bots still beat that opponent; jish_9 earns less. The selected release enables only the two preflop behavior gates, retaining original call thresholds and betting margins.

Balanced real/stress improvement (bb/duplicate deal): **+0.0794 [+0.0202, +0.1385]**.
With the newer AdaptiveProfit (main4) excluded: **+0.0686 [+0.0061, +0.1310]**.
Real-field change: +0.0514 [-0.0132, +0.1160]. Stress-field change: +0.1073 [+0.0283, +0.1863].
Real-field points change/match: +0.0208 [-0.0114, +0.0531]. Direct versus jish_4: +0.0000 [+0.0000, +0.0000].

## Preventing fixation on one opponent

The selection score gives 50% weight to six real bots and 50% to eight stress styles. Newer AdaptiveProfit accounts for only 1/12 of the score. Each candidate was tested on two development seeds. Variants with a positive development score excluding main4 were eligible first. Two additional real bots (jish_2 and rebuilt jish_6) and two synthetic styles were reserved for confirmation. No bot identity enters the strategy.
The selected source was frozen before eight independent fresh seed blocks, with no further strategy selection using those results. Promotion requires positive evidence both with and without main4, plus checks for regressions and tournament points.

## Selected strategy

Configuration: `{'_BUTTON_OPEN': 0.48, '_MARGIN_SCALE': 1.0, '_CALL_DISCOUNT': 0.0, '_STYLE_ADAPTIVE': False, '_AVOID_MARGINAL_REPOP': True, '_PASSIVE_ISOLATION': True}`.
The experiments isolate higher button opening thresholds (more limping), lower minimum gains for betting, and a bounded call discount. Adaptive variants use only half-local public action counts to preserve steals versus folders and require evidence of aggression before widening calls. The final settings above identify which features are active.
A call discount allows calls below estimated pot odds. This is an empirical allowance for estimation error and future play, not a mathematically justified discount to true pot odds. It can lose money if the equity estimate is accurate. Lower betting margins likewise trade caution for more marginal bets. Validation, rather than theoretical claims, determines promotion.
Two additional development experiments tested public-action gates: avoiding marginal opening raises against observed relentless re-raisers, and lowering the big-blind value-raise threshold only after sufficient evidence of both checking and calling with very few folds or raises. These changes were developed before any confirmation result was inspected.
The preflop model, numerical evaluator, range-learning foundation, game rules, and server protocol remain inherited from jish_4. Earlier versions are preserved.

## Paired confirmation by opponent

| Opponent | jish_4 bb/deal | jish_9 bb/deal | Change [95% interval] | Points change/match |
|---|---:|---:|---|---:|
| jish_4 | +0.0000 | +0.0000 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| main3 | +0.2774 | +0.2956 | +0.0182 [-0.1650, +0.2015] | +0.125 |
| main4 | -1.0349 | -0.8756 | +0.1593 [-0.1088, +0.4273] | +0.000 |
| quad2 | +2.7694 | +2.7694 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| pocketedge2 | +1.8372 | +1.8372 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| pokerbot2 | +1.8433 | +1.9743 | +0.1310 [-0.1956, +0.4576] | +0.000 |
| jish_2 | +0.0705 | +0.0705 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| jish_6 | +1.5854 | +1.5854 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| pot | +4.1082 | +4.1087 | +0.0004 [-0.3257, +0.3266] | +0.000 |
| station | +11.6102 | +12.2943 | +0.6841 [+0.4707, +0.8975] | +0.000 |
| nit | +1.7982 | +1.9181 | +0.1199 [+0.0243, +0.2155] | +0.000 |
| pressure | -0.1124 | -0.1124 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| trapper | +1.7818 | +1.7818 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| polar | +3.3225 | +3.3225 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| switcher | +1.2557 | +1.3097 | +0.0540 [-0.1675, +0.2755] | +0.062 |
| random | +9.4138 | +9.4138 | +0.0000 [+0.0000, +0.0000] | +0.000 |
| delayed_pot | +11.2357 | +10.8122 | -0.4235 [-0.5633, -0.2837] | +0.000 |
| station_maniac | +8.7897 | +8.7897 | +0.0000 [+0.0000, +0.0000] | +0.000 |

Each policy faced each opponent on the same deals, with fresh half-local state. Confidence intervals use eight independent seed-block means (Student-t, df=7), not individual hands treated as independent. Per-opponent intervals are exploratory, without multiple-comparison correction. Constant observed point differences can produce zero-width intervals; these do not establish zero future risk. These results describe this field and seeds, not superiority against every possible opponent.

The held-out opponents do not contribute to the primary score, but participate in the regression checks. Previously studied opponents are not new unseen strategies; only their confirmation deals are fresh.

## Official HTTP matches

| Opponent | Result | bb/deal | 95% judge interval |
|---|---|---:|---|
| jish_4 | CHOP | +0.0000 | [+0.0000, +0.0000] |
| main4 | AGENT2_WIN | -1.1150 | [-1.9161, -0.3139] |
| pocketedge2 | AGENT1_WIN | +2.1955 | [+1.5003, +2.8907] |
| jish_2 | CHOP | -0.0190 | [-0.4737, +0.4357] |
| pot | AGENT1_WIN | +5.0220 | [+3.3215, +6.7225] |
| nit | AGENT1_WIN | +2.2155 | [+1.6941, +2.7369] |
| trapper | AGENT1_WIN | +1.2745 | [+0.3737, +2.1753] |
| switcher | AGENT1_WIN | +2.2350 | [+0.8895, +3.5805] |
| delayed_pot | AGENT1_WIN | +12.1235 | [+10.6136, +13.6334] |
| main3 | CHOP | +0.2010 | [-0.1593, +0.5613] |
| quad2 | AGENT1_WIN | +2.2100 | [+1.3528, +3.0672] |
| pokerbot2 | AGENT1_WIN | +1.9550 | [+1.2022, +2.7078] |
| jish_6 | AGENT1_WIN | +1.6130 | [+0.9129, +2.3131] |
| station | AGENT1_WIN | +11.9535 | [+10.8997, +13.0073] |
| pressure | AGENT2_WIN | -1.3335 | [-2.3133, -0.3537] |
| polar | AGENT1_WIN | +2.2110 | [+1.1644, +3.2576] |
| random | AGENT1_WIN | +9.3500 | [+7.8130, +10.8870] |
| station_maniac | AGENT1_WIN | +9.1315 | [+7.7565, +10.5065] |

Across both sides: 0 errors, 0 forfeited halves, 0 exhausted time banks. Maximum jish_9 charged half 1.103/8 seconds; maximum startup 1.683/15 seconds. Direct confirmation fallbacks: 0.

All scored matches use official 40BB stacks and duplicate-deal rules. HTTP checks restart processes between halves and enforce the official request/time-bank/error rules. Docker is unavailable locally: a clean tournament-container build and isolated CPU/memory limits remain unverified. Direct-engine timing is diagnostic only.
Edge tests include exact PLO evaluation, short stacks, raise caps, evidence gates, half resets, and bounded policy changes. No model training or opponent-state information carries across match halves.

```
..............................................                           [100%]
=============================== warnings summary ===============================
../../work/venv/lib/python3.14/site-packages/fastapi/testclient.py:1
  /Users/josh/Documents/Codex/2026-11-07/https-github-com-tamu-datathon-org-2/work/venv/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
46 passed, 1 warning in 11.69s
```

## Predeclared promotion rule

All unit and official HTTP checks pass, no fallbacks. Across eight fresh seed blocks, the 95% Student-t intervals for balanced real/stress improvement AND the same score excluding main4 must be wholly positive. Real-field and stress-field mean improvements must both be nonnegative; real-field match-point improvement interval must be nonnegative. No opponent may show a clear regression worse than 0.25 bb/duplicate deal (upper 95% bound below -0.25), including held-out opponents. No clearly negative head-to-head against jish_4. Otherwise publish experimental and retain jish_4. No further candidate selection using final results.

Clear material regressions under that rule: ['delayed_pot']. Absence of a detected regression does not prove equivalence.
