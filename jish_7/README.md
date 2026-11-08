# jish_7 — team quad-j

A separate copy of jish_4 with tested betting-margin and blocker-model changes. Read BOT_NOTES.md and validation/REPORT.md for the release decision; a higher version number does not establish greater strength.

Keep the entire folder, including data/preflop.npy. From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PORT=5008 python agent.py
```

Run checks with `python -m pytest -q`. With another bot on port 5009, use a third terminal:

```sh
source .venv/bin/activate
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed comparison-7 --json match-result.json
```

Each match is 2,000 hands using 1,000 duplicate deals. Restart both bot processes before another match. Docker build checking requires Docker: ./tools/check_build.sh.
