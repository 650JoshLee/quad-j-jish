# jish_6 — research-spec rebuild

Team **quad-j**. Built from RESEARCH_SPEC.txt, the official participant guide, and the clean official starter. Earlier bots are test opponents only; no earlier strategy code or trained equity table is included.

This is **40BB short-deck five-card pot-limit Omaha**, not 100BB no-limit Hold'em. See RULE_ADAPTATIONS.md and PROVENANCE.json for adaptations and source hashes.

## Run

From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PORT=5008 python agent.py
```

**Keep the entire folder**, including `data/research_opening.npy`. This 1.5MB table was freshly generated from legal PLO simulations. Committed offline model data is permitted; no runtime downloads are used. Use normal Git, not Git LFS.

With another bot listening on port 5009, use a third terminal in this folder:

```sh
source .venv/bin/activate
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed research-comparison --json match-result.json
```

A match covers 1,000 duplicate deals / 2,000 hands. Restart both bot processes before another match. Supply AGENT1_TOKEN / AGENT2_TOKEN if authentication is enabled.

## Check

```sh
python -m pytest -q
./tools/check_build.sh
```

The build check needs Docker. Test results and runtime limitations appear in validation/REPORT.md. The repository root continues to run jish_4; this replacement is published separately for comparison.
