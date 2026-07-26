# Did the game's temper change after breaks? (cards — descriptive)

Every other result in this project rests on shots. The claim that breaks 'cool the game down' or 'break its rhythm' is different in kind, and cards test it directly: they proxy tempo, aggression and game control, which no shot metric captures.

Rates are yellow cards per minute, both teams. Post-break windows start at resumption. Each break is differenced against the mean of its own matched control pool (equal weight per break); paired differences bootstrapped by match.

| w | breaks | matches | pre rate | post rate | change (real) | change (matched) | **D** | 95% CI |
|---|---|---|---|---|---|---|---|---|
| 5 | 196 | 102 | 0.023 | 0.019 | -0.0041 | +0.0006 | **-0.0047** | [-0.0217, +0.0124] |
| 8 | 196 | 102 | 0.022 | 0.020 | -0.0019 | +0.0017 | **-0.0036** | [-0.0180, +0.0103] |
| 10 | 196 | 102 | 0.024 | 0.023 | -0.0015 | +0.0033 | **-0.0049** | [-0.0174, +0.0077] |

**Every interval includes zero.** Booking rates after breaks are indistinguishable from those after matched ordinary minutes: on this measure the breaks neither calmed the game nor stirred it up.

## Why goals are NOT an outcome here

Goals are time-stamped and more numerous than cards (308 vs 253), so they look like the better outcome. They cannot be used with this control pool. Test A's preregistered screen excludes candidate minutes within 3 minutes of a goal, so control windows are goal-depleted **by construction**:

| | goals per 8-min window |
|---|---|
| real break windows | 0.227 |
| matched control windows | 0.054 |

That four-fold gap is the screen, not the breaks. Reporting it would have produced a dramatic false positive. Red cards and VAR reviews are excluded from the control pool for the same reason and are additionally far too rare (15 each). Yellow cards are not screened, and their base rates are comparable across arms, which is why they are the one additional outcome this design can carry.

## Why there is no build-up or positional version of this table

The FIFA post-match reports do contain rich tactical data — line height, team length, build-up phases, line breaks, passing networks, defensive pressure. Every page of six reports (~300 pages) was scanned for a half split, minute bin or per-period breakdown: **none exists**. Those metrics are one value per team per match, so a before/after-break comparison is not a difficult analysis, it is an undefined one. StatsBomb's 2018/2022 data does carry true event coordinates, but those tournaments had no universal breaks.

## Limits

- Descriptive. Cards depend on referee behaviour, score state and match importance; this is an association at matched moments, not a causal claim.
- Sparse: ~0.16 cards per 8-minute window, so intervals are wide and only a large effect would be detectable.
- Yellow cards only. Reds and VAR are too rare and are control-screened.
