# quad-j / jish_11

A separate jish_4-based experiment with raise-size response learning, low-equity raise evaluation, and an explicit opponent re-raise response estimate. All older bots are preserved. **Experimental: jish_4 remains the default.**

Testing covered 487,200 hands. The balanced field change versus jish_4 was -0.0557 bb/duplicate deal (95% interval [-0.1226, +0.0112]); overall improvement is unproven. Official HTTP results: 16 wins, 3 draws, 3 losses, with zero errors, forfeits, or exhausted banks. Targeted size-sensitive folding and bet-then-fold opponents showed clear gains, but these did not justify promotion.

Read [strategy notes and limitations](BOT_NOTES.md) and [validation results](validation/REPORT.md) before choosing a tournament submission. Keep `data/preflop.npy` with this bot.

From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PORT=5008 python agent.py
```

Run another bot on port 5009. In a third terminal with the same environment:

```sh
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed jish11-comparison --json match-result.json
```

Restart both servers between matches. Set AGENT1_TOKEN and AGENT2_TOKEN if authentication is enabled. For checks:

```sh
python -m pytest test_agent.py tests -q
```

The local environment has no Docker. Official HTTP testing is a local runtime check, not certification of a clean tournament container or different hardware.
