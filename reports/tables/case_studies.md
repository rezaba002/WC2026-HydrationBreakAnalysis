# Case studies — transparent 2x2 selection (Core Output 7)

Scored breaks: 183 of 203 (20 unscored: no eligible pseudo-break minutes).
Axis 1: |Δ shot balance| across the break, percentile vs the same match/half's ordinary minutes. Large ≥80th, small ≤50th.
Axis 2: did the perception pilot find a public claim naming that break?

## Population

| cell | breaks |
|---|---|
| confirmed_feeling | 5 |
| perception_illusion | 5 |
| hidden_effect | 66 |
| true_null | 71 |
| mid | 36 |
| unscored | 20 |

Breaks with a public claim in the pilot: **14 of 203**. Breaks with an equally large measured swing and no pilot claim: **66**.

**How to read that asymmetry.** Collection combined a topical pass with a
PRE-SPECIFIED STRATIFIED RANDOM SWEEP of 24 matches / 48 breaks, each searched
with an identical query template (`data/manual/perception_sweep_log.csv`). The
sweep is the unbiased estimate: **4 of 48 breaks (8.3%, 95% Wilson CI
3.3-19.6%) drew a public claim**, which extrapolates to roughly 17 of 203
breaks (CI 7-40). The topical pass adds claims from outside the sample, so the
raw `has_claim` count below exceeds what the sweep rate alone implies.
For unswept matches `has_claim=False` still means 'no claim located', not
'nobody ever said anything' — the sweep exists precisely so the denominator
does not rest on that assumption.

## Selected cases

| case type | fixture | stage | break | minute | disruption | pctile | claimed |
|---|---|---|---|---|---|---|---|
| confirmed_feeling | Panama v England | Group Stage | 2 | 69' | 8 | 100 | yes |
| confirmed_feeling | Germany v Curaçao | Group Stage | 1 | 23' | 5 | 100 | yes |
| hidden_effect | Morocco v Haiti | Group Stage | 2 | 68' | 6 | 100 | no |
| perception_illusion | Austria v Jordan | Group Stage | 2 | 72' | 0 | 9 | yes |
| perception_illusion | England v Congo DR | Round of 32 | 1 | 23' | 0 | 14 | yes |
| true_null | South Korea v Czechia | Group Stage | 2 | 70' | 0 | 0 | no |

## Selection rule (applied, not curated)
- 2 confirmed-feeling, 1 hidden effect (the three large-swing cases);
- 2 perception illusion, 1 true null (the three small-swing cases);
- within each cell, ranked by percentile then disruption; one case per match.
- No case was chosen because it was famous. Netherlands-Sweden,
  Germany-Curacao and Switzerland-Bosnia were the planning-stage favourites;
  they qualify only if the matrix puts them there.

## Reading
- **Panama v England (2nd break) moved cells when the sweep ran.** It was the
  flagship 'hidden effect' — Panama went from 1 shot to England's 3 before the
  break, to 6 against England's 0 after it, the tournament's largest pressure
  inversion, while still losing 0-2. The systematic sweep then found TNT Sports
  had reported exactly that dip. It is now a confirmed-feeling case. This is the
  provisional caveat in the earlier version doing its job: 'no claim found' was
  correctly not treated as 'no claim exists'.
- 'Hidden effect' cases remain the largest cell by far: dozens of breaks with
  swings as large as the famous ones, with no located commentary.
- Planning-stage favourites qualified on merit, not reputation: Germany-Curacao
  and Netherlands-Sweden both scored at the 100th percentile; Switzerland-Bosnia
  still did not make the selection.
- 'Perception illusion' cases carry a public claim while the swing sits inside
  the ordinary range for that same match-half.
- Each case still needs a manual tactical review before it goes in the report;
  the matrix picks WHICH matches to review, not what to conclude.
