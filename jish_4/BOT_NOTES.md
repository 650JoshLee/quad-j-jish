# jish_4 — quad-j

A separate copy of jish_2 with one focused bet-selection correction. The original jish_1, jish_2, and jish_3 source and model files were preserved.

## Change

The safety margin is now applied once against checking/calling. Among raises that clear that margin, the bot chooses the highest estimated value. Previously, a half-pot raise could clear the margin and then a more valuable pot raise would need to clear an additional margin before being chosen. The change avoids that order-dependent comparison.

The equity engine, opponent model, preflop data, and server plumbing are unchanged. This is a focused policy correction, not a new large model-training run. It was deliberately bounded to conserve the remaining assistance allowance.

## Verification

All **25 tests passed**, including a new regression case where half-pot and capped pot both qualify, but the larger raise has greater estimated value. Four development matches against jish_2 were draws. The final round robin used a fresh deal seed.

## Final eleven-bot round robin

55 matches, 110,000 hands, 10 matches per bot. jish_4 placed **3**, with **7 wins, 3 draws, 0 losses**, **8.5 points**, and **+30,542 net chips**.

jish_2 placed 2 with 9.0 points and +28,791 net chips. Their head-to-head result was **CHOP**, with -0.004 bb per duplicate deal for jish_4. Here the raw AGENT1/AGENT2 verdict refers to the saved matchup's entrant order; inspect validation/head-to-head.json for identities.

These are results from one seeded local run. They do not establish superiority on future deals. Read validation/REPORT.md for all match results, runtime limits, duplicate PocketEdge entries, and the Jesse Park adapter qualification.

## Start on this computer

From this jish_4 folder:

```sh
PORT=5013 ../../work/venv/bin/python agent.py
```

With jish_2 running on 5010, use a second terminal in this folder:

```sh
../../work/venv/bin/python judge_engine.py --agent1 5013 --agent2 5010 --deals 1000 --seed your-fresh-seed --logs --json comparison.json
../../work/venv/bin/python tools/count_hands.py comparison.json
```

For a portable installation, create a Python environment and install requirements-dev.txt as documented in the starter README. Preserve data/preflop.npy with agent.py.

No paid services or GitHub push were used. Docker validation remains pending on a machine with Docker running.

Current name: jish_4. Team: quad-j. Embedded validation files keep their historical match names; see ../BOT_NAMES.md.
