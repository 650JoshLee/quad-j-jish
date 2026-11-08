# jish_11 — quad-j

A preserved copy of jish_4 with three targeted changes. The evaluator, preflop model, official game and server remain inherited from jish_4. This is not based on the independent jish_10 solver.

1. **Raise-size response learning.** Separate fold/call/re-raise observations for actual small and large raises. Stack-capped actions are classified by their actual size. Counts are shrunk toward the existing opponent model using 32 prior observations, with limited sharing between postflop streets. Terminal folds/calls are recorded when the opponent had a genuine raising option. All memory resets each half.
2. **Evaluate raises before folding.** A hand below the original calling threshold may still raise if the estimated raise value clears the existing uncertainty margin versus folding. The original call threshold stays intact. This does not force bluffs or lower the threshold for ordinary calls.
3. **One opponent re-raise.** A raise's continuation value now includes an estimated re-raise range, exact legal half/pot re-raise amounts and our best estimated fold/call response. The new estimate is blended with the original one-step estimate to limit reliance on an uncertain opponent model. Unavailable re-raises at the cap or all-in are excluded.

## Limitations

This is still a heuristic equity bot, not a full poker solver. The response tree ends after one opponent re-raise and our fold/call response; it does not model our further raises or future streets explicitly. Opponent re-raise sizes use an equal mixture of half-pot and pot. Range selection still largely relies on current made-hand ranks, so draw quality is imperfectly represented. Two size buckets cannot capture every position, board, or bet-history interaction. Sparse observations may be misleading despite shrinkage. Original cumulative learning and fixed preflop thresholds remain.

All three changes are implemented in the released experiment. Development compares single-feature versions diagnostically and selects between light and fuller combinations before fresh confirmation. Publication does not imply promotion. See validation/REPORT.md for results and the default decision.
