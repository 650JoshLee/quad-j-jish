# jish_2 — quad-j

This is a separate improved copy of jish_1. The original source and equity data in the sibling `quad-j` folder were preserved. Nothing was pushed to GitHub.

## What changed

The original equity evaluator, preflop lookup, simulation budget, betting policy, and server plumbing are retained. The new strategy interprets opponent checks more carefully:

- It combines the original cautious check model with a model consistent with the opponent's observed betting frequency.
- It learns how strong checked hands actually were when the opponent reveals cards at showdown. Evidence of slow-playing reduces the assumption that a check means weakness.
- Sparse evidence is shrunk toward a cautious prior. All learning resets each half and uses only legal observations and revealed cards.

Showdown examples are selected by the betting, so these statistics are useful evidence rather than an unbiased measurement of every checked hand. The bot remains an approximate opponent model, not a solved equilibrium strategy.

## Professional tactics studied

[Phil Galfond's analysis of a heads-up hand against Chance Kornuth](https://www.cardplayer.com/poker-news/26982-pot-limit-omaha-strategy-phil-galfond-breaks-down-hand-from-his-match-with-chance-kornuth) illustrates how checks can preserve strong hands, how blockers change plausible ranges, and how earlier actions constrain later value bets and bluffs. The transferable lesson used here is to interpret checks in the context of an opponent's behavior. Known-card removal was already handled by the original simulations.

[Upswing's PLO strategy booklet](https://upswingpoker.com/wp-content/uploads/2018/05/10_Pot_Limit_Omaha_Secrets_Exposed_2018.pdf) discusses protecting checking ranges, position, and selecting hands that perform well against callers. These were hypotheses to test, not opening charts to copy: the tournament uses a 36-card deck, five hole cards, unusual hand rankings, shallow stacks, and no elimination-based tournament pressure.

Explicit re-raise forecasting, next-card draw modeling, and alternative preflop policies were tested during development. They were omitted from the release because they did not improve broad performance consistently enough to justify the added computation. The selected version is the simpler, calibrated check model.

## Results

See `COMPARISON.md` for the full scorecard and limitations.

- Ten independent matches against original jish_1: **6 wins, 4 draws, 0 losses**, over 20,000 hands.
- Mean head-to-head edge: **+0.596 bb per duplicate deal**, 95% interval **[+0.442, +0.750]**.
- Twelve other opponent styles over two fresh seeds: **22 wins, 2 draws, 0 losses**, matching the original's match points. Aggregate chip performance against that field was statistically indistinguishable from the original.
- Two additional real HTTP matches against original jish_1 were wins. All four supplied baselines were also beaten through HTTP.
- **24 tests passed**. All twelve final HTTP halves had zero errors, timeouts, forfeits, or skipped decisions. Maximum charged thinking time was **0.642 of 8 seconds**; maximum startup was **1.302 of 15 seconds**, on this computer.

The evidence supports an advantage over original jish_1, not guaranteed superiority against every opponent. Keep both versions.

## Run alongside the original

On this computer, from the `jish_2` folder, use the already tested environment:

```sh
PORT=5010 ../../work/venv/bin/python agent.py
```

The original can continue running on port 5008. In another terminal, also from `jish_2`:

```sh
../../work/venv/bin/python judge_engine.py --agent1 5010 --agent2 5008 --deals 1000 --seed your-new-seed --logs --json comparison.json
../../work/venv/bin/python tools/count_hands.py comparison.json
```

Here agent 1 is jish_2 and agent 2 is original jish_1.

For a portable installation, use Python 3.12 or the locally tested Python 3.14:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
PORT=5010 python agent.py
```

Keep `data/preflop.npy` with `agent.py`; it is required. The preflop data is unchanged: 65,536 simulations per suit-equivalent holding, covering all 376,992 holdings. No downloads are needed during play.

## Reproduce the comparisons

From this folder with the chosen environment activated:

```sh
python tools/arena.py --reference ../quad-j/agent.py --opponents original --seeds fresh-1 fresh-2 --output validation-extra.json
python tools/arena.py --reference ../quad-j/agent.py --seeds fresh-field-1 --output field-extra.json
python tools/compare_original.py --reference ../quad-j/agent.py --seeds fresh-http-1 --output validation-extra-http
```

The arena uses the actual game engine directly. The HTTP comparison tool starts and stops its own servers and restarts both bots for each half. It needs the original folder to be present; the new bot itself is independent of that folder.

## Container check still required

Docker was unavailable, so the container build could not be certified. The requirements and Dockerfiles are unchanged from jish_1; prior Linux/Python 3.12 dependency resolution succeeded, but does not replace a container test. On a machine with Docker running:

```sh
./tools/check_build.sh
```

Raw match results, timing, tests, source/data checksums, and preservation verification are under `validation/`.

Current name: jish_2. Team: quad-j. Embedded validation files keep their historical match names; see ../BOT_NAMES.md.
