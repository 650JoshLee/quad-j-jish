# jish_1 — quad-j

A local tournament bot for heads-up Short Deck PLO5. The submission entry point is `agent.py`; keep `data/preflop.npy`, `requirements.txt`, and the original game/evaluator files with it. Nothing has been committed or pushed.

## Strategy

- **Preflop:** a lookup for all 376,992 five-card holdings. Suit symmetry reduces training to 19,998 classes. Each class uses 65,536 uniformly sampled legal opponent hands and boards, for 1,310,588,928 offline simulations. These are Monte Carlo estimates, not exact solved equities. Reproducible generation details are in `data/preflop_metadata.json`.
- **Postflop:** compiled Monte Carlo evaluates 768 candidate opponent hands with three runouts each; on the river it uses 1,536 candidates with the actual board. Samples exclude every known card. The evaluator enforces exactly two hole cards and three board cards, the short-deck wheel, flush over full house, and trips over straight.
- **Opponent adaptation:** public action history shifts the candidate range. Observed betting, folding, and revealed showdown strength adjust how informative aggression is. Forced calls at the raise cap do not count as evidence of passivity.
- **Actions:** use pot odds, estimated equity against the current range, estimated equity against callers, position, stack depth, and legal raise sizes. The bet comparison is a one-step approximation with an allowance for future betting, not an equilibrium solver.
- **Reliability:** all mutable learning and random state reset in `new_half`. Static lookup tables are read-only in use. Numerical compilation happens before the web server starts. Sample counts decrease if measured compute costs grow. The original server plumbing, referee, and reference evaluator are unchanged.

## Run locally

Use Python 3.12 (the tournament version) or Python 3.14 (the locally tested version). From this directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python agent.py
```

The bot listens on port 5008 by default. The existing `PORT` and `AGENT_TOKEN` settings remain supported. The initial import compiles the numerical routines; no network access or model download is needed during play.

For a match, start an opponent in another terminal and run the judge:

```sh
.venv/bin/python baseline-bots/baseline_random.py
# In a third terminal:
.venv/bin/python judge_engine.py --deals 1000 --seed 47
```

The local development environment used for this delivery is outside the repository, under the workspace's `work/venv` directory. It is not included in the archive or container.

## Final validation

All 20 tests passed. Tests include exhaustive comparison of every legal five-card lookup against the referee, 2,000 random Omaha showdowns, exact-two-card and suit-symmetry checks, legal sampling, exact river sample outcomes, half reset behavior, a nut-hand value bet, forced-call accounting, and the original HTTP compatibility tests. Tests reported one upstream FastAPI/Starlette deprecation warning; there were no test failures.

The following results use the actual HTTP judge, 1,000 duplicate deals / 2,000 hands per opponent, seed `held-out-http-47`, and newly started servers for each half. Values are **big blinds per duplicate deal**, combining both seats, as reported by the judge.

| Supplied opponent | Mean bb/duplicate deal | Result |
| --- | ---: | --- |
| Random | +8.011 | Win |
| Calling station | +11.428 | Win |
| Always pot | +3.334 | Win |
| Always half | +4.139 | Win |

Every win's 95% confidence interval was above zero. Across all eight halves: zero errors, zero timeouts, zero forfeits, and zero skipped decisions. Maximum charged thinking time was approximately 0.68 seconds of the 8-second bank. Measured cold startup was 1.14–1.15 seconds against the 15-second limit. These timings are local measurements, not measurements on the tournament's CPU.

Additional direct-engine matches on a separate seed, `held-out-strategy-93`, beat three simple card-aware opponents: tight (+0.875), balanced equity (+2.643), and loose (+5.082) bb per duplicate deal. Each used 2,000 hands and had a positive 95% confidence interval. The benchmark policies are available for inspection in `tools/benchmark.py`. These opponents are development checks; they do not establish performance against unknown tournament entrants.

Raw judge results, confidence intervals, startup measurements, smoke-test output, and test output are in `validation/`.

## Remaining build check

**The Docker image has not been validated here.** `tools/check_build.sh` could not run because Docker was unavailable. Dependency resolution did succeed for Linux x86-64 / Python 3.12 using binary wheels, but this is not a substitute for the container test.

On a machine with Docker running, run:

```sh
./tools/check_build.sh
```

The original tournament Dockerfiles are unchanged. The added `.dockerignore` excludes local caches and validation reports while retaining the required equity data. No paid services or external training data were used.

## Reproduce or extend

```sh
# Rebuild preflop estimates (not needed to run the supplied bot):
.venv/bin/python tools/train_preflop.py --samples 65536

# Direct-engine strategy benchmarks:
.venv/bin/python tools/benchmark.py --deals 1000 --seed new-validation-seed

# Full HTTP matches, restarting each server for every half:
.venv/bin/python tools/validate_matches.py --output validation-new --seed new-http-seed
```

The source bundle was downloaded from [tamu-datathon-org/heads-up-bundle](https://github.com/tamu-datathon-org/heads-up-bundle) at commit `c83ab6eeb7660a2fd1fae7df224315d41fe985a9`. Constraints were checked against the supplied [participant guide](https://docs.google.com/document/d/1D1ruabeQ25scYg97ehBMnzA9fqaEWWsnFDfOmrLme4E/edit).

Current name: jish_1. Team: quad-j. Embedded validation files keep their historical match names; see ../BOT_NAMES.md.
