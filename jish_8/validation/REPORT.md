# jish_8 — extreme-opponent optimization of jish_4

**520,000 test hands:** 20,000 diagnostic, 84,000 candidate-development, 384,000 frozen confirmation, and 32,000 official HTTP judge hands.

**Keep jish_4 as the default. Publish jish_8 as experimental; the promotion criteria were not all met.**

Balanced real/stress field change, bb/duplicate deal: **+0.0364 [-0.1283, +0.2012]** (95% seed-block interval).
Real-bot field change: -0.0151 [-0.2476, +0.2174]; stress field change: +0.0880 [-0.0256, +0.2016].
Real-field points change/match: -0.0208 [-0.0744, +0.0327]. Direct versus jish_4: -0.0662 [-0.3886, +0.2563].

## Strategy changes

- Opponent action counts retain 99% of their previous weight at each new observed hand. This responds faster to style changes while retaining prior smoothing.
- A second or later opponent raise on the same street applies half the likelihood exponent. Repeated raises are treated as correlated evidence, not independent confirmations of strength.
- Checks become less informative as an opponent approaches checking every opportunity.
- Calls become less informative as an opponent approaches never folding. Call selectivity is separated from raise frequency.
- Preflop data, numerical evaluator, betting-value calculations, server interface, and official rules remain inherited from jish_4. Earlier bots were preserved byte-for-byte. These are heuristic opponent-model changes, not a solved equilibrium.

## Paired fresh-deal confirmation

| Opponent | jish_4 bb/deal | jish_8 bb/deal | Change [95% interval] | Points change/match |
|---|---:|---:|---|---:|
| jish_4 | +0.0000 | -0.0662 | -0.0662 [-0.3886, +0.2563] | +0.083 |
| main3 | +0.3083 | +0.0510 | -0.2573 [-0.5611, +0.0464] | -0.167 |
| pocketedge2 | +1.7920 | +1.7103 | -0.0817 [-0.2616, +0.0983] | +0.000 |
| pokerbot2 | +1.8849 | +2.2297 | +0.3447 [-0.4409, +1.1304] | +0.000 |
| pot | +4.2058 | +4.2643 | +0.0586 [-0.0694, +0.1866] | +0.000 |
| half | +5.2041 | +5.1526 | -0.0515 [-0.1386, +0.0356] | +0.000 |
| station | +11.8903 | +11.8940 | +0.0037 [-0.2055, +0.2128] | +0.000 |
| fold | +1.4992 | +1.4988 | -0.0003 [-0.0012, +0.0005] | +0.000 |
| nit | +1.6783 | +1.7444 | +0.0662 [-0.0533, +0.1857] | +0.000 |
| pressure | -0.0965 | -0.1988 | -0.1023 [-0.3155, +0.1108] | +0.000 |
| trapper | +1.8076 | +2.7916 | +0.9840 [+0.7810, +1.1870] | +0.000 |
| polar | +3.4612 | +3.6747 | +0.2135 [-0.3804, +0.8074] | +0.000 |
| switcher | +1.0531 | +1.3903 | +0.3372 [-0.2002, +0.8747] | +0.167 |
| random | +9.7089 | +9.0799 | -0.6290 [-1.3036, +0.0456] | +0.000 |
| delayed_pot | +11.6803 | +11.6052 | -0.0752 [-0.3159, +0.1656] | +0.000 |
| station_maniac | +8.9378 | +8.9770 | +0.0392 [-0.2182, +0.2965] | +0.000 |

The selection compared five modified configurations plus the original-policy control on one development seed. The selected configuration was frozen before six fresh seed blocks. Each block contains both policies against the same 16 opponents on identical deals. State resets between halves. Confidence intervals use six independent block means (Student-t, df=5), not individual hands as independent trials.

The primary field gives 50% weight to four real bots and 50% to ten synthetic stress styles. The two additional styles, delayed_pot and station_maniac, were excluded from selection and the primary score. Per-opponent intervals are exploratory, without multiple-comparison correction. A constant observed points change can yield a zero-width interval; it does not prove zero future risk. These estimates apply to this field and seeds, not all possible opponents.

Synthetic styles cover constant pot and half-pot raises; never-raise calling stations; folding to every bet; tight value play; attacks on checks; traps; polarized betting; alternating aggression/tightness; random actions; postflop-only relentless aggression; and 50-hand station/maniac switches.

## Official HTTP judge and edge cases

| Opponent | Result | bb/deal | 95% judge interval |
|---|---|---:|---|
| jish_4 | CHOP | -0.1880 | [-0.6182, +0.2422] |
| pocketedge2 | AGENT1_WIN | +1.5555 | [+0.8999, +2.2111] |
| pot | AGENT1_WIN | +5.1025 | [+3.4178, +6.7872] |
| station | AGENT1_WIN | +11.4025 | [+10.3627, +12.4423] |
| nit | AGENT1_WIN | +1.9845 | [+1.5225, +2.4465] |
| trapper | AGENT1_WIN | +2.9155 | [+2.1457, +3.6853] |
| switcher | AGENT1_WIN | +1.9595 | [+0.6769, +3.2421] |
| delayed_pot | AGENT1_WIN | +11.0735 | [+9.5557, +12.5913] |
| main3 | CHOP | -0.1690 | [-0.6633, +0.3253] |
| pokerbot2 | AGENT1_WIN | +1.3020 | [+0.5870, +2.0170] |
| half | AGENT1_WIN | +6.5000 | [+4.8638, +8.1362] |
| fold | AGENT1_WIN | +1.5000 | [+1.5000, +1.5000] |
| pressure | CHOP | +0.3160 | [-0.6395, +1.2715] |
| polar | AGENT1_WIN | +3.6775 | [+2.7064, +4.6486] |
| random | AGENT1_WIN | +9.8805 | [+8.3210, +11.4400] |
| station_maniac | AGENT1_WIN | +9.1105 | [+7.7467, +10.4743] |

Runtime across both sides: 0 errors, 0 forfeited halves, 0 exhausted banks. Maximum jish_8 charged half 0.975/8 seconds; maximum startup 1.458/15 seconds. Direct confirmation fallbacks: 0.

Tests cover all five-card evaluation scores, exact two-hole-card use, legal samples, state reset, raise selection, extreme range inference, and complete hands at 3/5/9/80-chip starting stacks. Short-stack configurations are robustness unit tests; all scored matches use the official 80-chip/40BB stacks.

Test output:
```
.............................................                            [100%]
=============================== warnings summary ===============================
../../work/venv/lib/python3.14/site-packages/fastapi/testclient.py:1
  /Users/josh/Documents/Codex/2026-11-07/https-github-com-tamu-datathon-org-2/work/venv/lib/python3.14/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
45 passed, 1 warning in 11.74s
```

The official judge used fresh processes for each half, 1,000 duplicate deals, the one-second request limit, eight-second time bank, and five-error rule. A circular import in the synthetic-opponent HTTP adapter initially prevented its startup; the adapter was corrected before those scored matches. Candidate code was unchanged. Docker is unavailable locally: CPU/memory isolation and a clean tournament-container build remain unverified. Direct-engine timing is diagnostic only.

## Promotion rule

Require all tests and official HTTP checks to pass; 95% Student-t interval across six seed blocks for the equally weighted real/stress field improvement wholly positive; real-field mean positive and corresponding point-change interval nonnegative; no significant regression versus jish_4 or either held-out stress style. Otherwise retain jish_4 as default. No further selection on confirmation results.
