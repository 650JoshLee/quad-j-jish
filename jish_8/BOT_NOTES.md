# jish_8 strategy notes

Copied from jish_4; all earlier strategies are preserved. This experiment targets the information inferred from opponent actions rather than increasing Monte Carlo precision or adopting the inconclusive jish_7 changes.

Selected settings:
- Action-count decay: 0.99 per newly observed hand, with existing Bayesian prior smoothing.
- Second and later raises on one street: likelihood exponent 0.5.
- Check likelihood: attenuated when observed aggression is below 35%.
- Call likelihood selectivity: tied to observed folding, reaching full strength at 40% folds.

These thresholds were compared as a small, explicit configuration search. They are heuristic approximations, not calibrated probabilities or claims of optimal play. A change's theoretical plausibility is not evidence of stronger tournament performance; consult the fresh-deal comparison.

The no-change development control reproduces jish_4 policy. Candidate selection uses an equally weighted aggregate of four real opponents and ten stress styles. Two additional styles are excluded from selection. Six fixed fresh seed blocks assess the chosen version; a separate official HTTP run checks legality, timing, errors, and forfeits.

All mutable opponent evidence is kept in per-half memory and wiped by new_half. Sampling excludes known cards. Model files and the score evaluator are unchanged from jish_4. Existing preflop play, raise value calculation, and server implementation are retained.

See validation/REPORT.md for all results, uncertainty intervals, runtime limitations, and the promotion rule.
