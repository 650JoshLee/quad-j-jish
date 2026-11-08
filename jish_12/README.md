# quad-j / jish_12

Final conservative candidate based on a separate copy of jish_4. **Experimental: final validation did not establish broad improvement, so jish_4 remains the default.** Every previous version is preserved.

Keep `data/preflop.npy` with `agent.py`. See [strategy notes](BOT_NOTES.md) and [final validation](validation/REPORT.md).

Testing covered 667,200 hands against a 32-opponent confirmation/runtime field. Balanced primary-field change versus jish_4 was -0.0668 bb/duplicate deal, with a 95% seed-block interval of [-0.1948, +0.0613]. All 38 local tests passed; official HTTP results were 21 wins, 9 draws, 2 losses, with zero errors, forfeits or exhausted banks. Both jish_4 and jish_12 passed the official constrained Linux container build/smoke check.

The targeted size-folder and bet-then-fold opponents improved, but the deceptive-history opponent exposed a -0.2300 bb/deal regression, 95% interval [-0.3154, -0.1446]. The guarded changes are not a universal improvement.

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
