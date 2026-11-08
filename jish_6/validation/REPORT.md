# jish_6 — independent research-spec rebuild

Built only from the supplied research text, official participant guide, and clean official starter. Older bots were executed as test opponents only. No prior strategy code or trained model was reused.

## Final official-judge comparisons

This is a 14-opponent comparison suite for jish_6, not a fresh all-versus-all round robin. Each opponent played 1,000 duplicate deals / 2,000 hands with new processes per half. The final seed was fixed after the preflop-context correction.

| Opponent | Result for jish_6 | Net chips | bb/duplicate deal | 95% interval |
|---|---|---:|---:|---|
| Jesse Park / Flush Theory | Win | +4,803 | +2.401 | [+1.531, +3.272] |
| PocketEdge (1) | Draw | +673 | +0.337 | [-0.235, +0.908] |
| PocketEdge (2) | Draw | +482 | +0.241 | [-0.326, +0.808] |
| PokerBot main3 / Active Guard | Loss | -2,275 | -1.137 | [-1.897, -0.378] |
| PokerBot main3 / Previous Champion | Draw | +689 | +0.344 | [-0.119, +0.808] |
| PokerBot-Team-quad-j | Draw | -140 | -0.070 | [-0.545, +0.405] |
| PokerBot-Team-quad-j (2) | Draw | +621 | +0.310 | [-0.157, +0.778] |
| jish_1 | Loss | -2,616 | -1.308 | [-2.035, -0.581] |
| jish_2 | Draw | -1,133 | -0.567 | [-1.299, +0.166] |
| jish_3 | Loss | -1,973 | -0.987 | [-1.715, -0.258] |
| jish_4 | Loss | -1,697 | -0.849 | [-1.587, -0.110] |
| jish_5 | Draw | +583 | +0.291 | [-0.412, +0.995] |
| pokerbot | Win | +5,203 | +2.602 | [+1.857, +3.346] |
| pokerbot2 | Win | +1,689 | +0.845 | [+0.225, +1.464] |

**3 wins, 7 draws, 4 losses; 6.5/14 points; +4,909 net chips.**

jish_6: 0 errors, 0 forfeited halves, 0 exhausted time banks. Maximum charged half 1.334/8 seconds; maximum startup 1.450/15 seconds.

Opponents: 0 errors, 0 forfeited halves, 0 exhausted time banks.

The 18-test suite passed, covering the official web interface, exact Omaha scoring on 5,400 partial/full board cases, legal card sampling, suit-invariant opening estimates, per-half memory, and preflop opening-versus-reraise context.

## Sources and adaptations

- User research: RESEARCH_SPEC.txt (100BB no-limit Hold’em principles). See RULE_ADAPTATIONS.md for every major conversion to 40BB short-deck PLO.
- Official starter: https://github.com/tamu-datathon-org/heads-up-bundle at c83ab6eeb7660a2fd1fae7df224315d41fe985a9. This matches the current upstream main commit checked during this build.
- Official guide: https://docs.google.com/document/d/1D1ruabeQ25scYg97ehBMnzA9fqaEWWsnFDfOmrLme4E/edit , refreshed through text export.
- New model: 19,998 suit classes × 8,192 independently seeded trials = 163,823,616 legal simulated showdowns. Expanded to all 376,992 holdings. No older equity table was reused.
- All game/evaluator/judge files and server plumbing match the official starter. Only the editable strategy block, bot identity, additional dependencies and package documentation were changed.

## Limitations and release decision

jish_4 remains the repository default as requested. This is an independent implementation of the supplied research principles; it is not a solved equilibrium and is not presented as a demonstrated upgrade to jish_4. The comparison suite is one seeded sample, with per-match intervals not adjusted for multiple comparisons.

The official HTTP judge enforced decision and half time limits. Tests ran two independent matches concurrently on the local computer; Docker CPU/memory isolation was not used. The official build check was attempted and stopped because Docker was unavailable. No successful clean-container build is claimed.

PocketEdge (1) and (2) are identical source/model submissions. Previous Champion is identical to PokerBot-Team-quad-j (2); duplicates were retained as in the requested opponent field. Jesse Park is Flush Theory with the existing interface/chip/raise-size adapter; its native straight-above-trips logic is preserved, while the official referee awards trips above straights.

Development suite A predates the preflop-context correction and is stored separately; those scores are not final-version results. Fresh final suite B uses research-spec-holdout-B. The earlier four simple practice styles are development diagnostics, not final HTTP certification.
