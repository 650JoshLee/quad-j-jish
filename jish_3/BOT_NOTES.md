# jish_3 — quad-j

This is a separate experimental copy of jish_2. Original jish_1 (`quad-j`) and jish_2 code and model files were preserved and their fingerprints verified. Nothing was pushed to GitHub.

**The extra training and numerical accuracy are verified. A playing-strength improvement over jish_2 is not established by the release tests. Keep jish_2 as your comparison baseline.**

## Extra training

The initial table used 65,536 trials per suit-equivalent starting-hand class. This iteration adds **914,882,560 offline trials** for 3,490 classes near important decision thresholds. Those classes now have **327,680 trials each**; other classes retain the initial estimates. Suit symmetry still covers all 376,992 possible five-card holdings.

`data/preflop.npy` is the refined model. `data/preflop_initial.npy` preserves the initial table for reproduction. Counts, seeds, selection thresholds, and the initial table metadata are in `data/preflop_metadata.json`.

## More precise card calculations

The default method samples possible opponent hands and evaluates every legal future board for each sample: **253 possible turn/river combinations on the flop** and **22 river cards on the turn**. On the river, it enumerates **all 65,780 legal opponent holdings**. Shared two-card evaluations make this practical while respecting exactly two hole cards and three board cards.

A compute-budget controller reduces sample counts and switches to a cheaper sampler when measured costs are high. Consequently, exhaustive calculations are conditional on the available compute allowance. Card enumeration is exact within the chosen mode; the opponent's betting range is still inferred by an approximate behavioral model.

The previous opponent-adaptation and betting policy are retained. Starting-hand thresholds, re-raise settings, value-betting margins, and learning priors were tested in development. No retune showed sufficient consistent benefit to replace the conservative defaults. Numerical accuracy alone need not improve chip results when the betting model is approximate.

The prior research on [Phil Galfond's heads-up analysis against Chance Kornuth](https://www.cardplayer.com/poker-news/26982-pot-limit-omaha-strategy-phil-galfond-breaks-down-hand-from-his-match-with-chance-kornuth) and [Upswing's PLO strategy material](https://upswingpoker.com/wp-content/uploads/2018/05/10_Pot_Limit_Omaha_Secrets_Exposed_2018.pdf) informs the range-based approach. Standard PLO examples are not calibrated opening charts for this 36-card, five-hole-card game.

## Release results

See `COMPARISON.md` for score tables, confidence intervals, limitations, and the downloaded opponent identities.

- Against jish_2, 40,000 hands: **3 match wins, 17 draws, 0 losses**. Aggregate advantage **+0.008 bb per duplicate deal**, 95% interval **[-0.075, +0.091]**. This is statistically inconclusive.
- Against original jish_1, 12,000 hands: **3 wins, 3 draws, 0 losses**, average **+0.595 bb per duplicate deal**.
- Fourteen opponent styles over two fresh seeds: **26 wins, 2 draws, 0 losses**. jish_2 scored the same match points on the same deals; aggregate field chip difference was also inconclusive.
- In actual HTTP matches, jish_3 beat the downloaded PokerBot-Team-quad-j submission, PocketEdge v2, original jish_1, and a calling station. Two additional HTTP matches against jish_2 were draws.
- **31 tests passed.** All twelve final HTTP halves completed with zero errors, timeouts, forfeits, or skipped decisions for either bot. Maximum charged thinking time: **3.958/8 seconds**. Maximum startup: **2.169/15 seconds**, locally.

This version uses more compute than jish_2. It has not demonstrated an upgrade in overall competitive strength, despite lower estimation noise and additional training. No result guarantees success against an unknown entrant.

## Start it on this computer

Open Terminal in the new folder and use the already tested environment:

```sh
PORT=5012 ../../work/venv/bin/python agent.py
```

This leaves ports 5008 and 5010 available for original jish_1 and jish_2. To compare against jish_2 running on 5010, use another terminal in jish_3:

```sh
../../work/venv/bin/python judge_engine.py --agent1 5012 --agent2 5010 --deals 1000 --seed your-fresh-seed --logs --json comparison.json
../../work/venv/bin/python tools/count_hands.py comparison.json
```

Here agent 1 is jish_3. Keep both server terminals open.

## Portable setup

Use Python 3.12 (the tournament version) or the locally tested Python 3.14:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
PORT=5012 python agent.py
```

The bot needs `agent.py`, its requirements, `data/preflop.npy`, and the original evaluator/game helpers. No internet or model download is needed while playing. All match-specific learning stays in memory and resets each half.

## Reproduce training or tests

With the selected environment activated, from jish_3:

```sh
# Reproduce the refined table from the included initial table:
python tools/refine_preflop.py --base data/preflop_initial.npy --output data/preflop.npy

# Fresh direct-engine comparisons:
python tools/arena.py --reference ../jish_2/agent.py --opponents original --seeds fresh-1 fresh-2 --output validation-extra.json

# Real HTTP match; this tool starts and stops both servers itself:
python tools/http_match.py --agent2 ../jish_2/agent.py --seed fresh-http-1 --output validation-extra-http
```

The downloaded opponents are not redistributed in the archive. Their isolated test copies are in this workspace's `work/new2-opponents`. PocketEdge's downloaded macOS library was blocked by system policy; its supplied C source was compiled locally in that test copy. No downloaded source or original binary was changed. The compiled native engine was used for the final results.

## Container check still required

Docker was unavailable here. The local HTTP tests and dependency checks do not certify the tournament container. On a machine with Docker running, execute this from jish_3 before submission:

```sh
./tools/check_build.sh
```

Requirements, original Dockerfiles, and server plumbing are unchanged. No paid services were used.

Current name: jish_3. Team: quad-j. Embedded validation files keep their historical match names; see ../BOT_NAMES.md.
