# jish_5 independent strategy research

Reviewed public professional match analyses, not a scraped hand-history training dataset or inaccessible paid videos:

- Phil Galfond, firsthand heads-up PLO against Chance Kornuth: https://www.cardplayer.com/poker-news/26982-pot-limit-omaha-strategy-phil-galfond-breaks-down-hand-from-his-match-with-chance-kornuth
  Actions constrain ranges across streets. Holding blockers to opponents' calling hands can favor checking strong hands; unblocked bluffs can favor inducing. Implementation: blocker-conditioned sampled holdings, full-history likelihood, separately valued check-induce branch.
- Doug Polk vs Daniel Negreanu, two public heads-up hands: https://upswingpoker.com/polk-vs-negreanu-two-bluffs-analyzed/
  Heads-up ranges are wide, and pressure depends on plausible value and semi-bluff ranges. Implementation: a mixture of five opponent policies, moderate bluff floors, draw-street continuation, opponent-dependent response branches.

These examples use ordinary-deck four-card PLO or no-limit hold'em, not this short-deck five-card variant. No professional opening charts or pot sizes were transplanted. New opening estimates were generated independently under the official game rules. The bot is a heuristic approximation, not a solved equilibrium or a neural model trained on these players.

Architecture differs from jish_1–4: prime-product evaluation, new offline simulations, latent opponent-policy mixture, whole-history particle likelihood, explicit fold/call/re-raise response branches, check-induced value, range-wide response decisions. Only official interface, evaluator reference scoring, and referee modules are reused. Previous data and decision functions are not imported.

## Development and release

Fresh offline model: 19,998 suit classes × 8,192 trials = 163,823,616 legal simulated showdowns, expanded to all 376,992 holdings. No previous equity table was reused.

Development: 48,000 hands in a six-configuration search, 48,000 hands in an independent three-configuration validation, and 24,000 hands in follow-up checks. The release uses {'value_margin': 0.045, 'future_tax': 0.18, 'induce': 0.3, 'range_power': 0.95}. Initial search preceded the final-response learning correction; later validation included it.

This independent architecture has not demonstrated superiority to jish_2: its selected configuration lost on the independent validation sample. Keep all previous versions. Final performance is reported in ../round-robin-jish5/REPORT.md.

15,000 evaluator comparisons, 500 suit-isomorphism checks, and 600 legal-game trajectory hands passed, plus the 12 official HTTP interface tests. The final tournament uses a separate deal seed and frozen source copies.

## Final tournament result

In the fresh 12-bot / 66-match / 132,000-hand round robin, jish_5 ranked 5, with 3 wins, 8 draws, 0 losses, 7.0 points, and +5,008 net chips across 22,000 hands. All four head-to-head matches against earlier jish versions were draws. This run does not support replacing the higher-ranked earlier versions with jish_5.

Full table, confidence intervals, hand counts, raw half-results, and adapter qualifications: ../round-robin-jish5/REPORT.md. Tournament totals: 0 errors, 0 forfeited halves, 0 exhausted time banks.
