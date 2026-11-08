# jish_12 — final conservative adjustment experiment

This version copies jish_4, preserving its evaluator, preflop model and established value/call decisions. It does not import jish_10's solver or jish_11's re-raise branch.

The candidate implementation records responses by street, actual raise size, and whether our raise faced a bet. Optional contextual learning changes the old response estimate only after a minimum number of relevant observations and a sizable estimated departure from the old model. Estimates remain shrunk toward the existing model. Optional bluff evaluation considers a raise below the calling threshold only when a conservative lower estimate of the observed fold frequency exceeds a pure-bluff break-even threshold plus the original betting margin. Ordinary call thresholds stay unchanged.

These evidence gates are heuristics. Their intervals do not guarantee profitability against changing opponents, correlated observations, adaptive sampling or opponents who deliberately manipulate their history. They are intended to reduce needless changes against opponents that the baseline already handles well.

Development compares five new configurations and the control. The highest-scoring new configuration is frozen before fresh confirmation; the final release may enable only the supported feature combination. See PROVENANCE.json and validation/REPORT.md for the selected flags and results.

## Known remaining limitations

- No full multi-street game-tree search or equilibrium guarantee.
- Range likelihoods still largely rank made hands, imperfectly representing strong draws and blockers.
- Existing cumulative statistics can lag a changing opponent; targeted fast-switch and deceptive-history opponents test this risk.
- Fixed preflop thresholds and approximate equity-realization adjustments remain.
- Showdown learning is selected by betting history, not an unbiased sample.
- Sparse Monte Carlo estimates and aggressive reweighting may have low effective sample size; no formal per-decision error bound is claimed.
- Missing or invalid model data fails startup; the data folder is required.

Passing tests does not prove that every weakness has been eliminated. The audit and validation report distinguish verified properties, measured performance and unresolved deployment limits.
