# Adapting the supplied research to this tournament

Sources: RESEARCH_SPEC.txt; the official participant guide; official starter commit c83ab6eeb7660a2fd1fae7df224315d41fe985a9. No earlier bot strategy or trained table was reused.

| Research topic | Tournament implementation |
|---|---|
| 100BB no-limit Hold'em | Heads-up 40BB short-deck five-card pot-limit Omaha |
| Two-card hand charts, low offsuit hands, A2–A5 bluffs | Fresh simulated equities for all 376,992 legal five-card holdings, ranks 6–A |
| Any number of private cards usable in Hold'em | Exactly two private plus three community cards, scored against the official evaluator |
| Standard hand order | Flush above full house; trips above straight; A6789 is the low straight |
| Arbitrary bets, overbets, unrestricted jams | Only legal CHECK_CALL/FOLD/RAISE_HALF/RAISE_POT; exact judge-provided raise totals |
| Top-pair stack-offs at low SPR | No automatic pair commitment; use PLO equity, price, remaining stacks, and future pressure |
| Frequent dry-board continuation bets | Board texture and estimated PLO equity/continuing ranges inform betting; the Hold'em claim that most flops miss both hands is not assumed |
| Range reasoning and position | Sampled opponent holdings, public-history range likelihood, wider positional opening and better equity realization in position |
| Balanced value/bluffs and mixed actions | Bounded blocker/draw bluffs, protected checking ranges, randomized near-equivalent choices |
| Pot odds, MDF, bluff ratios | Correct call price; MDF is a reference rather than a compulsory call rate against all ranges; opponent call price caps bluff mixing |
| Small-sample exploitation warning | Shrunk action statistics, at least 60 observations before deviations grow, bounded adjustment strength |
| Memory and randomness | All learning/RNG reset each half; no runtime internet, no hidden judge cards, no cross-half state |

The policy is a heuristic adaptation, not a computed Nash equilibrium. Hand estimates come from fresh legal simulations; the opening table's values are Monte Carlo estimates, not exhaustive probabilities. Range/nut advantage and drawing potential are approximations. MDF alone cannot make an arbitrary PLO policy unexploitable.

The official HTTP server, game, evaluator and judge remain unchanged. Compiled numerical scoring is checked against the official evaluator. The Google guide was refreshed through its text export; source hashes are in PROVENANCE.json.
