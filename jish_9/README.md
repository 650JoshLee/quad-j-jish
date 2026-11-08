# quad-j / jish_9

A separate jish_4 copy for official heads-up, 40BB, short-deck five-card pot-limit Omaha. Earlier versions are preserved.

**Experimental; jish_4 remains the default.** Testing covered 920,000 hands and 46 passing tests. The balanced chip-profit gain was positive, including with newer AdaptiveProfit excluded, but a held-out style showed a clear regression and tournament-point improvement was inconclusive. See the full report for this tradeoff. See [full validation](validation/REPORT.md) for results and the default/promotion decision.

The selected release enables two preflop adjustments based on public action history:
- After at least 12 facing-bet observations and an estimated raising rate above 78%, require at least 49.5% estimated equity for button opening raises, avoiding marginal raise-then-fold lines against relentless re-raisers.
- After at least 20 free-action and 20 facing-bet observations, with smoothed aggression below 10% and folding below 15%, lower the big-blind value-raise threshold from 56% to 52% estimated equity.

Original call thresholds, betting margins, model data, evaluator, range learning, and server protocol are retained. Learned behavior resets each half. Opponent identity is never used.

## Run

Keep this whole folder, including `data/preflop.npy`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PORT=5008 python agent.py
```

Start another bot on port 5009. In a third terminal from this folder:

```sh
source .venv/bin/activate
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed fresh-comparison --json comparison.json
```

To match tournament process isolation, run halves separately with the same seed and restart both servers between halves, then combine results.

## Verification

```sh
python -m pytest -q
```

Tests separate development from fresh confirmation and include results excluding the newer AdaptiveProfit. Docker is unavailable locally; a clean tournament-container build and isolated CPU/memory limits are not certified. With Docker available, run `./tools/check_build.sh`.

Official rules: https://github.com/tamu-datathon-org/heads-up-bundle
