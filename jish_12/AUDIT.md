# Final audit scope

This audit checks the implementation and tests plausible weaknesses. It cannot establish that every possible exploit has been found or that the bot is optimal.

| Area | Review or check | Disposition |
|---|---|---|
| Short-deck hand ranking | Exhaustive five-card lookup comparison and independent Omaha evaluator tests | Retained official ranking and exactly-two-hole/three-board rules |
| Deck sampling | Legal sampled opponent cards and river outcomes checked against reference | No duplicate/visible-card leakage in tested samples |
| Preflop model | Shape, dtype, finite values, suit invariance, file hash and packaging | Original jish_4 model retained; folder must include data/preflop.npy |
| Legal actions, cap, stacks | Official interface/engine tests and full HTTP matches | Original game and server unchanged |
| Early fold prevents bluff raises | Added evidence-gated alternative raise evaluation | Requires relevant observed folds to clear a conservative break-even check |
| Responses depend on context and size | Separate optional-response observations by street, facing-bet status and actual size | Gated/shrunk estimates reduce premature departures from baseline |
| Sparse or misleading evidence | Unit tests plus fast_switch, late_trap and alternating_sizes opponents | Empirical stress checks; no guarantee against arbitrary deception |
| Opponent re-raises | Revisited jish_11 result and existing penalties | Full re-raise branch not carried forward after broad regression; remains approximate |
| Draws, blockers, future streets | Reviewed existing sampler and range likelihoods | Equity sampling includes runouts, but range inference and future betting remain heuristic |
| Changing styles | Existing cumulative statistics inspected; switching opponents tested | Recency weighting not added without new evidence of broad benefit |
| Showdown learning | Revealed-card-only learning, half reset and sparse-data tests | Selection bias remains documented |
| Memory isolation | Deterministic reset and fresh-process HTTP halves | No learned state should cross halves |
| Fallbacks | Direct tests/matches record fallback_count; judge records protocol faults | Final report gives observed counts, rather than treating legal fallback as proof of correct reasoning |
| Dependencies | Python 3.12 Linux binary packages resolved/downloaded for pinned requirements | Build compatibility also checked separately in container CI when available |
| Container restrictions | Official tools/check_build.sh through standard GitHub Actions runner | Check recorded outcome before relying on it; local Docker unavailable |
| Startup/request/bank limits | Official smoke plus complete HTTP matches | Measurements apply to tested hardware; retain timing margin |
| Files and network | Model bundled; runtime strategy reads data and uses half-local memory only | Official container smoke uses no network, read-only root and /tmp limit |
| Original preservation | Hash all prior bot files and frozen candidate source | Verify after tests and before publishing final results |
| Selection and overfitting | Freeze after development; four fresh blocks, diverse opponents, individual regression checks | Known field is finite; no universal tournament-strength claim |

Official rules: https://github.com/tamu-datathon-org/heads-up-bundle and the supplied participant guide. The starter container uses Python 3.12, one CPU, 4 GB RAM, no runtime internet, read-only files except /tmp (512 MB), and a 3 GB added-image limit. Server stack versions are unchanged. Match checks use 40BB stacks, 1,000 duplicate deals, fresh processes per half, an 8-second bank, and the official request/error rules.

The container job uses only standard runners on the public repository. GitHub documents these as free: https://docs.github.com/en/actions/concepts/billing-and-usage . It is a validation workflow, not deployment or paid training.
