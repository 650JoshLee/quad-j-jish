# quad-j / jish_12

Final conservative candidate based on a separate copy of jish_4. **Experimental while final validation is in progress; jish_4 remains the default.** Every previous version is preserved.

Keep `data/preflop.npy` with `agent.py`. See [strategy notes](BOT_NOTES.md) and the final validation report when available.

From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PORT=5008 python agent.py
```

Run another bot on port 5009, then use a third terminal:

```sh
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed jish12-comparison --json match-result.json
```

Restart both servers between matches. If using authentication, set AGENT1_TOKEN and AGENT2_TOKEN for the judge. Tests:

```sh
python -m pytest test_agent.py tests -q
bash tools/check_build.sh
```

The second command needs Docker and performs the official constrained-container smoke test. Python 3.12 Linux dependency wheels were verified independently. Container and runtime results are reported separately; a passing local test is not a universal hardware guarantee.
