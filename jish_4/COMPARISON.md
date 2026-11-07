# Eleven-bot round robin

**55 matches · 110,000 hands · 20,000 hands per bot**

Each bot played every other bot once. Each match used 1,000 duplicate deals / 2,000 hands, fresh processes for each half, and the official 40-big-blind game. The same deal seed was used across all pairings.

## Standings

| Rank | Bot | W–D–L | Points | Net chips | Avg bb/duplicate deal |
|---:|---|---:|---:|---:|---:|
| 1 | jish_3 | 8–2–0 | 9.0 | +30,575 | +1.529 |
| 2 | jish_2 | 8–2–0 | 9.0 | +28,791 | +1.440 |
| 3 | jish_4 | 7–3–0 | 8.5 | +30,542 | +1.527 |
| 4 | jish_1 | 7–1–2 | 7.5 | +19,184 | +0.959 |
| 5 | PocketEdge (2) | 2–4–4 | 4.0 | -3,349 | -0.167 |
| 6 | PocketEdge (1) | 2–4–4 | 4.0 | -3,730 | -0.186 |
| 7 | PokerBot-Team-quad-j (2) | 2–4–4 | 4.0 | -5,389 | -0.269 |
| 8 | PokerBot-Team-quad-j | 2–4–4 | 4.0 | -7,003 | -0.350 |
| 9 | pokerbot2 | 2–4–4 | 4.0 | -7,270 | -0.363 |
| 10 | pokerbot | 1–0–9 | 1.0 | -30,281 | -1.514 |
| 11 | Jesse Park / Flush Theory | 0–0–10 | 0.0 | -52,070 | -2.603 |

W–D–L counts matches. Wins earn 1 point, draws 0.5, losses 0. A match is a win only when the official 95% confidence interval excludes zero, except that forfeits override chip results. Rankings use points first, then mean big blinds per duplicate deal; equal scores retain tied ranks.

## Head-to-head matrix

Read each cell from the row bot’s perspective: W = win, D = draw, L = loss, F = both forfeited.

| Bot | J | JN | J2 | PE1 | PE2 | PB | Q1 | Q2 | PB2 | JP | J3 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J | — | L | L | W | W | W | W | W | W | W | D |
| JN | W | — | D | W | W | W | W | W | W | W | D |
| J2 | W | D | — | W | W | W | W | W | W | W | D |
| PE1 | L | L | L | — | D | W | D | D | D | W | L |
| PE2 | L | L | L | D | — | W | D | D | D | W | L |
| PB | L | L | L | L | L | — | L | L | L | W | L |
| Q1 | L | L | L | D | D | W | — | D | D | W | L |
| Q2 | L | L | L | D | D | W | D | — | D | W | L |
| PB2 | L | L | L | D | D | W | D | D | — | W | L |
| JP | L | L | L | L | L | L | L | L | L | — | L |
| J3 | D | D | D | W | W | W | W | W | W | W | — |

### Entrant identities

| Code | Requested entrant | Reported bot name |
|---|---|---|
| J | jish_1 | quad-j / jish_1 |
| JN | jish_2 | quad-j / jish_2 |
| J2 | jish_3 | quad-j / jish_3 |
| PE1 | PocketEdge (1) | Datathon2026 / PocketEdge v2 |
| PE2 | PocketEdge (2) | Datathon2026 / PocketEdge v2 |
| PB | pokerbot | TeamName / TitForTatBot |
| Q1 | PokerBot-Team-quad-j | YOUR_TEAM_NAME / ShortDeckEquity |
| Q2 | PokerBot-Team-quad-j (2) | Team-quad-j / AdaptiveProfit |
| PB2 | pokerbot2 | YOUR_REGISTERED_TEAM_NAME / Maroon Equity |
| JP | Jesse Park / Flush Theory | Jesse Park (adapter) / Flush Theory |
| J3 | jish_4 | quad-j / jish_4 |

## Every match

The chip score and confidence interval below are for Bot A. Hand-win counts cover both halves.

| # | Bot A | Bot B | Winner | A bb/deal | 95% interval | A hands won | B hands won | Ties |
|---:|---|---|---|---:|---|---:|---:|---:|
| [1](matches/01-jish_1-vs-jish_2/result.txt) | jish_1 | jish_2 | jish_2 | -0.971 | [-1.446, -0.496] | 923 | 1015 | 62 |
| [2](matches/02-jish_1-vs-jish_3/result.txt) | jish_1 | jish_3 | jish_3 | -0.917 | [-1.345, -0.489] | 918 | 1017 | 65 |
| [3](matches/03-jish_1-vs-pocketedge1/result.txt) | jish_1 | PocketEdge (1) | jish_1 | +1.392 | [+0.728, +2.056] | 1066 | 881 | 53 |
| [4](matches/04-jish_1-vs-pocketedge2/result.txt) | jish_1 | PocketEdge (2) | jish_1 | +1.392 | [+0.728, +2.056] | 1066 | 881 | 53 |
| [5](matches/05-jish_1-vs-pokerbot/result.txt) | jish_1 | pokerbot | jish_1 | +2.223 | [+1.529, +2.917] | 1046 | 890 | 64 |
| [6](matches/06-jish_1-vs-quad1/result.txt) | jish_1 | PokerBot-Team-quad-j | jish_1 | +1.089 | [+0.432, +1.746] | 943 | 993 | 64 |
| [7](matches/07-jish_1-vs-quad2/result.txt) | jish_1 | PokerBot-Team-quad-j (2) | jish_1 | +1.387 | [+0.676, +2.098] | 828 | 1096 | 76 |
| [8](matches/08-jish_1-vs-pokerbot2/result.txt) | jish_1 | pokerbot2 | jish_1 | +1.565 | [+0.914, +2.217] | 1040 | 916 | 44 |
| [9](matches/09-jish_1-vs-jesse/result.txt) | jish_1 | Jesse Park / Flush Theory | jish_1 | +2.817 | [+1.922, +3.711] | 1240 | 713 | 47 |
| [10](matches/10-jish_1-vs-jish_4/result.txt) | jish_1 | jish_4 | Draw | -0.385 | [-0.892, +0.122] | 939 | 1001 | 60 |
| [11](matches/11-jish_2-vs-jish_3/result.txt) | jish_2 | jish_3 | Draw | +0.078 | [-0.268, +0.424] | 966 | 973 | 61 |
| [12](matches/12-jish_2-vs-pocketedge1/result.txt) | jish_2 | PocketEdge (1) | jish_2 | +1.452 | [+0.763, +2.141] | 1065 | 878 | 57 |
| [13](matches/13-jish_2-vs-pocketedge2/result.txt) | jish_2 | PocketEdge (2) | jish_2 | +1.452 | [+0.763, +2.141] | 1065 | 878 | 57 |
| [14](matches/14-jish_2-vs-pokerbot/result.txt) | jish_2 | pokerbot | jish_2 | +2.357 | [+1.547, +3.168] | 1033 | 895 | 72 |
| [15](matches/15-jish_2-vs-quad1/result.txt) | jish_2 | PokerBot-Team-quad-j | jish_2 | +1.466 | [+0.752, +2.180] | 1006 | 928 | 66 |
| [16](matches/16-jish_2-vs-quad2/result.txt) | jish_2 | PokerBot-Team-quad-j (2) | jish_2 | +1.650 | [+0.887, +2.413] | 872 | 1060 | 68 |
| [17](matches/17-jish_2-vs-pokerbot2/result.txt) | jish_2 | pokerbot2 | jish_2 | +1.899 | [+1.204, +2.595] | 1090 | 869 | 41 |
| [18](matches/18-jish_2-vs-jesse/result.txt) | jish_2 | Jesse Park / Flush Theory | jish_2 | +3.066 | [+2.132, +3.999] | 1268 | 687 | 45 |
| [19](matches/19-jish_2-vs-jish_4/result.txt) | jish_2 | jish_4 | Draw | +0.004 | [-0.375, +0.383] | 964 | 977 | 59 |
| [20](matches/20-jish_3-vs-pocketedge1/result.txt) | jish_3 | PocketEdge (1) | jish_3 | +1.300 | [+0.587, +2.013] | 1059 | 882 | 59 |
| [21](matches/21-jish_3-vs-pocketedge2/result.txt) | jish_3 | PocketEdge (2) | jish_3 | +1.326 | [+0.614, +2.038] | 1061 | 881 | 58 |
| [22](matches/22-jish_3-vs-pokerbot/result.txt) | jish_3 | pokerbot | jish_3 | +2.721 | [+1.931, +3.512] | 1047 | 884 | 69 |
| [23](matches/23-jish_3-vs-quad1/result.txt) | jish_3 | PokerBot-Team-quad-j | jish_3 | +1.621 | [+0.862, +2.380] | 1003 | 937 | 60 |
| [24](matches/24-jish_3-vs-quad2/result.txt) | jish_3 | PokerBot-Team-quad-j (2) | jish_3 | +2.333 | [+1.575, +3.091] | 902 | 1038 | 60 |
| [25](matches/25-jish_3-vs-pokerbot2/result.txt) | jish_3 | pokerbot2 | jish_3 | +1.996 | [+1.318, +2.675] | 1053 | 911 | 36 |
| [26](matches/26-jish_3-vs-jesse/result.txt) | jish_3 | Jesse Park / Flush Theory | jish_3 | +3.159 | [+2.235, +4.082] | 1262 | 690 | 48 |
| [27](matches/27-jish_3-vs-jish_4/result.txt) | jish_3 | jish_4 | Draw | -0.008 | [-0.402, +0.386] | 974 | 967 | 59 |
| [28](matches/28-pocketedge1-vs-pocketedge2/result.txt) | PocketEdge (1) | PocketEdge (2) | Draw | +0.000 | [+0.000, +0.000] | 954 | 954 | 92 |
| [29](matches/29-pocketedge1-vs-pokerbot/result.txt) | PocketEdge (1) | pokerbot | PocketEdge (1) | +1.495 | [+0.922, +2.068] | 1058 | 862 | 80 |
| [30](matches/30-pocketedge1-vs-quad1/result.txt) | PocketEdge (1) | PokerBot-Team-quad-j | Draw | +0.085 | [-0.253, +0.423] | 935 | 978 | 87 |
| [31](matches/31-pocketedge1-vs-quad2/result.txt) | PocketEdge (1) | PokerBot-Team-quad-j (2) | Draw | -0.336 | [-0.783, +0.111] | 753 | 1166 | 81 |
| [32](matches/32-pocketedge1-vs-pokerbot2/result.txt) | PocketEdge (1) | pokerbot2 | Draw | -0.256 | [-0.809, +0.298] | 808 | 1128 | 64 |
| [33](matches/33-pocketedge1-vs-jesse/result.txt) | PocketEdge (1) | Jesse Park / Flush Theory | PocketEdge (1) | +2.658 | [+1.878, +3.437] | 1246 | 712 | 42 |
| [34](matches/34-pocketedge1-vs-jish_4/result.txt) | PocketEdge (1) | jish_4 | jish_4 | -1.367 | [-2.086, -0.648] | 876 | 1071 | 53 |
| [35](matches/35-pocketedge2-vs-pokerbot/result.txt) | PocketEdge (2) | pokerbot | PocketEdge (2) | +1.631 | [+1.048, +2.213] | 1045 | 878 | 77 |
| [36](matches/36-pocketedge2-vs-quad1/result.txt) | PocketEdge (2) | PokerBot-Team-quad-j | Draw | +0.085 | [-0.253, +0.423] | 935 | 978 | 87 |
| [37](matches/37-pocketedge2-vs-quad2/result.txt) | PocketEdge (2) | PokerBot-Team-quad-j (2) | Draw | -0.336 | [-0.783, +0.111] | 753 | 1166 | 81 |
| [38](matches/38-pocketedge2-vs-pokerbot2/result.txt) | PocketEdge (2) | pokerbot2 | Draw | -0.174 | [-0.686, +0.337] | 847 | 1083 | 70 |
| [39](matches/39-pocketedge2-vs-jesse/result.txt) | PocketEdge (2) | Jesse Park / Flush Theory | PocketEdge (2) | +2.658 | [+1.878, +3.437] | 1246 | 712 | 42 |
| [40](matches/40-pocketedge2-vs-jish_4/result.txt) | PocketEdge (2) | jish_4 | jish_4 | -1.367 | [-2.086, -0.648] | 876 | 1071 | 53 |
| [41](matches/41-pokerbot-vs-quad1/result.txt) | pokerbot | PokerBot-Team-quad-j | PokerBot-Team-quad-j | -0.905 | [-1.437, -0.373] | 961 | 948 | 91 |
| [42](matches/42-pokerbot-vs-quad2/result.txt) | pokerbot | PokerBot-Team-quad-j (2) | PokerBot-Team-quad-j (2) | -1.369 | [-1.952, -0.785] | 835 | 1070 | 95 |
| [43](matches/43-pokerbot-vs-pokerbot2/result.txt) | pokerbot | pokerbot2 | pokerbot2 | -1.442 | [-2.003, -0.882] | 865 | 1054 | 81 |
| [44](matches/44-pokerbot-vs-jesse/result.txt) | pokerbot | Jesse Park / Flush Theory | pokerbot | +1.484 | [+0.661, +2.308] | 1151 | 797 | 52 |
| [45](matches/45-pokerbot-vs-jish_4/result.txt) | pokerbot | jish_4 | jish_4 | -2.482 | [-3.310, -1.653] | 880 | 1052 | 68 |
| [46](matches/46-quad1-vs-quad2/result.txt) | PokerBot-Team-quad-j | PokerBot-Team-quad-j (2) | Draw | -0.190 | [-0.591, +0.211] | 882 | 1011 | 107 |
| [47](matches/47-quad1-vs-pokerbot2/result.txt) | PokerBot-Team-quad-j | pokerbot2 | Draw | +0.060 | [-0.378, +0.498] | 907 | 1006 | 87 |
| [48](matches/48-quad1-vs-jesse/result.txt) | PokerBot-Team-quad-j | Jesse Park / Flush Theory | PokerBot-Team-quad-j | +1.980 | [+1.237, +2.724] | 1144 | 804 | 52 |
| [49](matches/49-quad1-vs-jish_4/result.txt) | PokerBot-Team-quad-j | jish_4 | jish_4 | -1.911 | [-2.658, -1.164] | 931 | 1005 | 64 |
| [50](matches/50-quad2-vs-pokerbot2/result.txt) | PokerBot-Team-quad-j (2) | pokerbot2 | Draw | +0.208 | [-0.273, +0.690] | 1073 | 844 | 83 |
| [51](matches/51-quad2-vs-jesse/result.txt) | PokerBot-Team-quad-j (2) | Jesse Park / Flush Theory | PokerBot-Team-quad-j (2) | +2.561 | [+1.716, +3.405] | 1229 | 707 | 64 |
| [52](matches/52-quad2-vs-jish_4/result.txt) | PokerBot-Team-quad-j (2) | jish_4 | jish_4 | -2.324 | [-3.143, -1.505] | 1037 | 905 | 58 |
| [53](matches/53-pokerbot2-vs-jesse/result.txt) | pokerbot2 | Jesse Park / Flush Theory | pokerbot2 | +2.401 | [+1.592, +3.209] | 1186 | 769 | 45 |
| [54](matches/54-pokerbot2-vs-jish_4/result.txt) | pokerbot2 | jish_4 | jish_4 | -2.178 | [-2.890, -1.466] | 885 | 1072 | 43 |
| [55](matches/55-jesse-vs-jish_4/result.txt) | Jesse Park / Flush Theory | jish_4 | jish_4 | -3.253 | [-4.196, -2.311] | 678 | 1280 | 42 |

## Compatibility and execution notes

- PocketEdge (1) and PocketEdge (2) have identical source and model fingerprints. They were retained as separate entrants as requested. Several bots adjust simulation work based on measured runtime, so identical source does not guarantee identical chip totals across separate runs.
- Jesse Park is represented by Flush Theory, as selected. Its original package uses 100-big-blind stacks and arbitrary bet sizes. The adapter scales chip units and maps requested raises to the nearest legal half-pot or pot action. Its native evaluator ranks straights above trips; that submitted logic was preserved, while the official referee awards trips above straights. This is an adapted entry, not a test under its native rules.
- The downloaded PocketEdge macOS libraries were rebuilt from their provided C source in isolated test copies so their native engine could load. Original downloaded files were not modified.
- Other bots ran from isolated copies with their original strategies and model files. Dependencies were supplied by the existing Python environment; startup and decision timing were measured by the official HTTP judge.
- All contestants used the same 8-second time bank per 1,000-hand half, 1-second request limit, and 5-error forfeit rule. Two independent matches ran concurrently on separate local ports. Each half restarted both bot processes.

Execution totals: **0 errors; 0 forfeited halves; 0 exhausted time banks**. Maximum charged time in a half: 3.647 seconds. Maximum startup: 2.036 seconds.

This is one seeded local round robin, not a guarantee of rankings on future deals. Runtime limits were enforced by the referee; Docker resource isolation was not used. Full per-half results and server logs are in matches/.

Deal seed: `round-robin-jish_1-new3-fresh-1`.
