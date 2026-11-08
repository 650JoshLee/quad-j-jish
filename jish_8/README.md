# quad-j / jish_8

A separate optimization copy of jish_4 for the official heads-up, 40BB, short-deck five-card pot-limit Omaha tournament. Existing jish versions are preserved.

**Experimental: jish_4 remains the default.** Across 520,000 test hands, jish_8 did not establish an overall improvement. All 45 tests passed; 16 official HTTP matches produced 13 wins and 3 draws with no errors, forfeits, or exhausted time banks.

This version changes opponent-range inference: recent action counts receive more weight, repeated raises on one street receive less weight, and routine checks/calls by very passive players convey less strength information. The selected configuration is frozen before fresh confirmation. See [full results](validation/REPORT.md) for the publication/default decision and statistical limits.

## Run

Keep this entire folder together, including `data/preflop.npy`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
PORT=5008 python agent.py
```

Start another bot in a separate terminal on port 5009. In a third terminal, from this folder:

```sh
source .venv/bin/activate
python judge_engine.py --agent1 5008 --agent2 5009 --deals 1000 --seed fresh-comparison --json comparison.json
```

For tournament-style timing, restart both bot servers between the two separately run halves. The judge supports `--half 1`, `--half 2`, then `combine`; use the same seed for both halves.

## Verification

```sh
python -m pytest -q
```

The final report separates development from confirmation and official HTTP runtime checks. Docker is unavailable on the development machine; a clean tournament-container build is not certified. With Docker available, run `./tools/check_build.sh`.

The bot uses only its observation, half-local memory, and bundled offline data. It needs no network access while playing. The official game requires exactly two hole cards and three board cards; flush beats full house, and trips beats straight. Neither the official engine nor the server protocol was changed.

Official starter and rules: https://github.com/tamu-datathon-org/heads-up-bundle
