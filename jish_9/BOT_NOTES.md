# jish_9 strategy notes

The release enables `_AVOID_MARGINAL_REPOP` and `_PASSIVE_ISOLATION`, two public-action gates for preflop raises. `_BUTTON_OPEN=.48`, `_MARGIN_SCALE=1`, `_CALL_DISCOUNT=0`, `_STYLE_ADAPTIVE=False` retain original decisions elsewhere. Disabled experiment controls remain for reproducibility.

Development examined ten modified configurations plus the original-policy control on two seeds. Six real bots and eight synthetic styles each share half the score. Newer AdaptiveProfit receives only 1/12 of total weight. Eligibility favors improvement even with that opponent excluded.

Eight fresh seed blocks compare both policies against 18 opponents, including two real bots and two styles withheld from selection. Promotion requires evidence with and without AdaptiveProfit, nonnegative real/stress means, a match-point check, and regression checks. Read validation/REPORT.md for the decision and uncertainty.

Thresholds are empirical heuristics, not equilibrium solutions or certainty about future opponent behavior. All scored matches use official 40BB rules. Short-stack unit tests are robustness checks only. All learned state resets between halves.
