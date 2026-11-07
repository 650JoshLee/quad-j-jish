# quad-j poker bots

The default bot at the repository root is **jish_4**, the winner of our latest local round robin. All five versions are preserved in their own folders with their required data files.

| Folder | Previous name | Strategy |
|---|---|---|
| jish_1 | jish | Original equity and opponent-range bot |
| jish_2 | jish_new | Learned interpretation of checks |
| jish_3 | jish_new_2 | Higher-precision equity estimates |
| jish_4 | jish_new_3 | Bet-selection correction; current default |
| jish_5 | New independent version | Opponent-policy mixture and response tree |

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

See [the latest full tournament table](tournament-results/REPORT.md): 12 bots, 66 matches, 132,000 hands. jish_4 finished first with 9.5 points; jish_5 finished fifth with 7 points. No errors, forfeits, or exhausted time banks occurred. These are results from one seed, not a guarantee of future rankings. The report documents the Jesse Park adapter and identical PocketEdge submissions.

Root code and model files match jish_4. Earlier strategies and data were retained. Individual bot notes explain their changes and historical tests. Docker verification requires Docker to be running: ./tools/check_build.sh. Local HTTP testing passed; a Docker build has not been certified.

Official rules: https://github.com/tamu-datathon-org/heads-up-bundle
