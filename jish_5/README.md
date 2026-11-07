# jish_5 — team quad-j

Keep the entire folder, including `data/opening_equity.npy`.

From this folder, install and start:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PORT=5008 python agent.py
```

In a second terminal, start the other bot on port 5009. In a third terminal, from this folder with the environment activated:

```sh
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed friends-test-1 --json match-result.json
```

The judge plays both halves: 2,000 hands using 1,000 duplicate deals. Restart both bots before a new match. If either bot uses an authentication token, supply the corresponding AGENT1_TOKEN / AGENT2_TOKEN to the judge.

The model is an offline-generated opening equity lookup, permitted by the participant guide. It is read locally; no network or disk writes are needed for decisions. Submit the entire folder in normal Git, not Git LFS.

See BOT_NOTES.md for strategy, research sources, validation and limitations. Earlier versions are in the adjacent jish_1 through jish_4 folders.
