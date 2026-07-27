# Appendix — exploratory yellow-card-rate analysis

**A weak, indirect signal. Not a measure of tempo, rhythm or game control.**
A booking is a referee decision, driven by referee thresholds and game-management style, tactical fouling, dissent, score state, match importance, and cards given late for an earlier incident. Card rates can move without the run of play changing, and the run of play can change without any card. This is included only because it is the one non-shot outcome in the 2026 layer that is both time-stamped and dense enough to test at all.

Rates are yellow cards per minute, both teams. Post-break windows start at resumption. Each break is differenced against the mean of its own matched control pool (equal weight per break); paired differences bootstrapped by match.

| w | breaks | matches | pre rate | post rate | change (real) | change (matched) | **D** | 95% CI |
|---|---|---|---|---|---|---|---|---|
| 5 | 194 | 102 | 0.024 | 0.020 | -0.0041 | -0.0006 | **-0.0035** | [-0.0210, +0.0141] |
| 8 | 183 | 101 | 0.023 | 0.021 | -0.0020 | +0.0033 | **-0.0054** | [-0.0234, +0.0120] |
| 10 | 148 | 92 | 0.024 | 0.024 | +0.0007 | +0.0046 | **-0.0039** | [-0.0226, +0.0145] |

**Every card-rate interval includes zero.** Booking rates after breaks are indistinguishable from those after matched ordinary minutes. Given the sparsity (~0.16 cards per 8-minute window) only a very large shift would be detectable, so this is weak evidence about booking RATES — NOT a finding that the breaks left the character of the game unchanged.

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

- **Appendix status.** Exploratory, descriptive, and a weak proxy: cards measure referee decisions, not the run of play. Not evidence about positional structure or tactical control.
- Sparse: ~0.16 cards per 8-minute window, so intervals are wide and only a large effect would be detectable.
- Yellow cards only. Reds and VAR are too rare and are control-screened.
- Confounded by referee thresholds, tactical fouling, dissent, score state and match importance, none of which are adjusted for here.
