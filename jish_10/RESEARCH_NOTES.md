# Independent jish_10 experiment

This is a new strategy on the official starter server. No earlier jish strategy implementation or trained data was copied. Earlier bots are test opponents only.

## Slumbot connection

Eric Jackson's [Slumbot NL paper](https://cdn.aaai.org/ocs/ws/ws0979/7044-30516-1-PB.pdf) describes counterfactual regret minimization and abstractions for heads-up poker. His [Slumbot research repository](https://github.com/ericgjackson/slumbot2019) documents CFR+, sampling, card/bet abstractions, and endgame solving.

jish_10 independently implements full-tree positive-regret matching with linearly weighted average strategies in a small current-street game. A player chooses actions for each private strength bucket while accounting for the opponent's possible future raises, calls, and folds. No Slumbot source, proprietary policy, or online play was used. This is not Slumbot transplanted to Omaha.

## Adaptation to tournament rules

All cards and betting transitions use the official 36-card, five-hole-card, exactly-two-hole/three-board game. Flush beats full house and trips beat straight. The tree includes legal half-pot and pot raises, minimum increments, stack limits, the four-raise cap, and the big blind's option after a limp. Equity sampling deals opponent cards and runouts without replacement. The five-card score table is freshly generated from the official evaluator at startup, not loaded from another bot.

## Approximations and limitations

Eight private strength buckets replace actual ranges. Public actions adjust heuristic range priors; these priors are not a trained equilibrium range model. Monte Carlo equity against uniformly sampled legal hands assigns our bucket. At the end of the current street, an approximate showdown payoff replaces future-street betting. Early-street equity is therefore an imperfect substitute for position, draws, blockers, and future equity realization. Re-solving separate streets does not establish a safe full-game equilibrium. Numerical convergence on the small model does not prove strong Omaha play.

The implementation is simultaneous positive-regret matching, inspired by CFR+, rather than a reproduction of every detail of the published Slumbot solver. An independent Kuhn poker check verifies game value and a best-response gap in a known small game. Broad opponent tests determine practical strength separately.

## Runtime and reproducibility

State resets each half. There is no runtime network access or persistent training state. Compiled numerical kernels warm up during startup. Computation adapts to measured time use; this can cause slight policy differences across machines. The official judge's HTTP checks, not direct timing estimates, determine runtime compliance on this machine. A Docker build has not been certified.
