# Professional heads-up examples and jish_7 hypotheses

[Phil Galfond's firsthand heads-up PLO hand against Chance Kornuth](https://www.cardplayer.com/poker-news/26982-pot-limit-omaha-strategy-phil-galfond-breaks-down-hand-from-his-match-with-chance-kornuth): his analysis considers how his cards remove opponents' calling hands and preserve potential bluffs. A strong hand can benefit from checking when a bet struggles to get paid. This motivates testing whether the caller model accounts for holdings removed by our cards, rather than assigning the strongest remaining holdings the same percentile regardless of blockers.

[Doug Polk versus Daniel Negreanu, public hand analysis](https://upswingpoker.com/polk-vs-negreanu-two-bluffs-analyzed/): the discussion emphasizes wide heads-up ranges, occasional preflop bluffs, and street-by-street analysis of aggression. These are considerations for evaluating ranges, not evidence that a specific bluff or frequency belongs in this tournament.

Their hands used different variants and stack depths. No opening chart or numerical betting frequency is transplanted. The tournament's official short-deck PLO rules remain authoritative. These sources motivate hypotheses; they do not establish that a proposed implementation is stronger.

Candidate changes are isolated and tested: uncertainty in bet-minus-check payoff on common simulation samples; an adaptive betting margin; and a public-board reference distribution for opponents' calling strength. The last change is a model approximation, not a complete reconstruction of an opponent's subjective range. All candidates start from a copy of jish_4, preserving the original.
