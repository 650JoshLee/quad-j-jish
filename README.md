# quad-j poker bots

The default bot at the repository root is **jish_4**, retained after subsequent candidates failed the broad-test promotion criteria. All versions are preserved in their own folders with their required data files.

| Folder | Previous name | Strategy |
|---|---|---|
| jish_1 | jish | Original equity and opponent-range bot |
| jish_2 | jish_new | Learned interpretation of checks |
| jish_3 | jish_new_2 | Higher-precision equity estimates |
| jish_4 | jish_new_3 | Bet-selection correction; current default |
| jish_5 | New independent version | Opponent-policy mixture and response tree |
| jish_6 | Research-spec rebuild | Fresh PLO simulations and mixed range strategy; separate comparison version |
| jish_7 | Optimization copy of jish_4 | Adaptive betting margins and public-board caller model; experimental |
| jish_8 | Extreme-opponent optimization copy of jish_4 | Recency-weighted action learning and revised range inference; experimental |
| jish_9 | Broad-field optimization copy of jish_4 | Evidence-gated preflop raises; experimental |
| jish_10 | Independent Slumbot-inspired experiment | Current-street regret-matching solver; experimental, weaker in validation |

All bots identify their team as quad-j and display their numbered bot name.

## Run the default bot

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PORT=5008 python agent.py
```

Keep the data folder with agent.py. The default bot reads data/preflop.npy. Bundled offline model/data files are allowed by the official participant guide; they must be committed normally, not through Git LFS.

To run another version, use its folder, for example:

```sh
cd jish_5
PORT=5009 ../.venv/bin/python agent.py
```

With bots listening on ports 5008 and 5009, run this in a third terminal from the repository root:

```sh
source .venv/bin/activate
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed comparison-1 --json comparison-result.json
```

A match covers 2,000 hands using 1,000 duplicate deals. Restart both bots before another match. If either bot uses authentication, set the matching AGENT1_TOKEN or AGENT2_TOKEN for the judge.

## Verification and results

```sh
python -m pytest -q
```

See [the archived 12-bot tournament table](tournament-results/REPORT.md): 12 bots, 66 matches, 132,000 hands. jish_4 finished first with 9.5 points; jish_5 finished fifth with 7 points. No errors, forfeits, or exhausted time banks occurred. These are results from one seed, not a guarantee of future rankings. The report documents the Jesse Park adapter and identical PocketEdge submissions.

Root code and model files match jish_4. Earlier strategies and data were retained. Individual bot notes explain their changes and historical tests. Docker verification requires Docker to be running: ./tools/check_build.sh. Local HTTP testing passed; a Docker build has not been certified.

Official rules: https://github.com/tamu-datathon-org/heads-up-bundle

## Research-spec jish_6

[jish_6](jish_6/README.md) was rebuilt from the supplied research, official guide, and clean starter, without earlier strategy code or trained models. Its final 14-opponent comparison covered 28,000 hands: 3 wins, 7 draws, 4 losses, with zero errors, forfeits, or exhausted time banks. It lost to jish_4, so **jish_4 remains the default**. See [source adaptations](jish_6/RULE_ADAPTATIONS.md), [provenance](jish_6/PROVENANCE.json), and [full results](jish_6/validation/REPORT.md). All 18 tests pass. Docker build verification remains unavailable on the local machine.

## jish_7 optimization experiment

[jish_7](jish_7/README.md) is a separate copy of jish_4 with uncertainty-aware betting and a blocker-sensitive caller-strength reference. Testing covered 284,000 hands. Paired confirmation averaged +0.0474 bb/duplicate deal over jish_4, with a 95% seed-block interval of [-0.0907, +0.1856]: improvement is inconclusive. The point-score comparison was also inconclusive. All 31 tests and six official HTTP runtime checks passed with no errors, forfeits, or exhausted time banks. **jish_4 remains the default.** See [full results](jish_7/validation/REPORT.md) and [professional-hand research notes](jish_7/RESEARCH_NOTES.md).

## jish_8 extreme-opponent experiment

[jish_8](jish_8/README.md) is another preserved copy of jish_4, with recent-action weighting and revised inference from repeated raises, routine calls, and passive checks. Testing covered **520,000 hands**, including constant raisers, calling stations, pressure bettors, traps, and changing styles. The equally weighted real/stress field change was +0.0364 bb/duplicate deal, with a 95% seed-block interval of [-0.1283, +0.2012]. Overall improvement is inconclusive, so **jish_4 remains the default**. The trapping test opponent showed a strong gain, but individual-opponent findings are exploratory. All 45 tests passed. Sixteen official HTTP matches produced 13 wins and 3 draws, with zero errors, forfeits, or exhausted banks. See [full comparisons and limitations](jish_8/validation/REPORT.md).

## jish_9 broad-field experiment

[jish_9](jish_9/README.md) adds two observed-behavior gates to preflop raises while retaining jish_4's calling and betting thresholds. **920,000 test hands** covered development, eight frozen confirmation blocks against 18 opponents, and official HTTP checks. The balanced real/stress chip improvement was +0.0794 bb/duplicate deal, 95% interval [+0.0202, +0.1385]. With newer AdaptiveProfit excluded it remained +0.0686 [+0.0061, +0.1310]. However, the held-out delayed-aggression bot exposed a -0.4235 bb/deal regression, and real-field tournament-point improvement was inconclusive. **jish_4 remains the default; jish_9 is experimental.** All 46 tests passed and final HTTP checks had zero errors, forfeits, or exhausted banks. See [full results and promotion criteria](jish_9/validation/REPORT.md).

## Independent jish_10 solver experiment

[jish_10](jish_10/README.md) independently applies Slumbot-inspired regret minimization to a small current-street Omaha abstraction. **235,600 test hands** included three development configurations, paired fresh comparisons against 19 opponents, and 19 official HTTP matches. Its balanced field performance was **2.6238 bb/duplicate deal worse than jish_4**, with a 95% seed-block interval of [-3.7140, -1.5337]. It lost both fresh direct matches to jish_4 and both to jish_8. Official HTTP results were 7 wins, 6 draws, 6 losses, with zero errors, forfeits, or exhausted banks. **jish_4 remains the default; jish_10 is experimental.** All 1,121 checked files in the prior local bots were preserved. See [results](jish_10/validation/REPORT.md) and [research/limitations](jish_10/RESEARCH_NOTES.md). No Slumbot policy or older jish strategy/model was copied.
