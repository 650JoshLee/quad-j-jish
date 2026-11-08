# quad-j / jish_10

Independent Slumbot-inspired research bot for the official heads-up short-deck five-card pot-limit Omaha tournament. **Experimental: keep jish_4 as the default.**

The new strategy samples legal Omaha hands and solves a small current-street betting game using positive-regret matching. It was built on the clean official server, without earlier jish strategy code or trained data. It does not use Slumbot's Hold'em policy or contact Slumbot during play.

See [research and limitations](RESEARCH_NOTES.md), [provenance](PROVENANCE.json), and [measured comparisons](validation/REPORT.md). The approximation omits future-street betting and should not be mistaken for a full-game equilibrium solution.

## Run

From this folder, with Python and the listed dependencies installed:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PORT=5008 python agent.py
```

No preflop.npy or downloaded model is needed. The small score table is generated from the official evaluator at startup.

## Verify

```sh
python -m pytest test_agent.py -q
python tools/verify_solver.py
```

The second command checks all five-card combinations, sampled Omaha evaluations, betting-tree transitions against the official game, and an independently evaluated Kuhn poker strategy. Passing it validates those implementation properties, not tournament strength.

For a match against another bot listening on port 5009:

```sh
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed jish10-comparison --json match-result.json
```

Restart both bot servers before another match. The official server supports authentication; if enabled, give the judge the matching AGENT1_TOKEN and AGENT2_TOKEN environment variables.

The local environment has no Docker, so a container build is not certified. Runtime benchmarks in the report are local official-judge checks rather than a hardware-independent guarantee.
