# Case studies — transparent 2x2 selection (Core Output 7)

Scored breaks: 196 of 203 (7 unscored: no eligible pseudo-break minutes).
Axis 1: |Δ shot balance| across the break, percentile vs the same match/half's ordinary minutes. Large ≥80th, small ≤50th.
Axis 2: did the perception pilot find a public claim naming that break?

## Population

| cell | breaks |
|---|---|
| confirmed_feeling | 2 |
| perception_illusion | 4 |
| hidden_effect | 65 |
| true_null | 73 |
| mid | 52 |
| unscored | 7 |

Breaks with a public claim in the pilot: **10 of 203**. Breaks with an equally large measured swing and no pilot claim: **65**.

**Caveat on that asymmetry — it is provisional.** The perception pilot ran a
TOPICAL search (four outlets writing about hydration breaks), not the per-match
sweep the codebook mandates for full collection. So `has_claim=False` means
'no claim surfaced in the pilot', NOT 'nobody ever said anything'. Absence of
evidence here is not yet evidence of absence; the 65 figure will move once the
systematic per-match sweep runs. What IS already solid: large post-break swings
are common (65+ breaks), while the swings that entered public narrative are few
— consistent with availability bias, pending the full sweep to size it properly.

## Selected cases

| case type | fixture | stage | break | minute | disruption | pctile | claimed |
|---|---|---|---|---|---|---|---|
| confirmed_feeling | Germany v Curaçao | Group Stage | 1 | 23' | 5 | 100 | yes |
| confirmed_feeling | Netherlands v Sweden | Group Stage | 1 | 23' | 4 | 100 | yes |
| hidden_effect | Panama v England | Group Stage | 2 | 69' | 8 | 100 | no |
| perception_illusion | Austria v Jordan | Group Stage | 2 | 72' | 0 | 7 | yes |
| perception_illusion | England v Congo DR | Round of 32 | 1 | 23' | 0 | 25 | yes |
| true_null | South Korea v Czechia | Group Stage | 2 | 70' | 0 | 0 | no |

## Selection rule (applied, not curated)
- 2 confirmed-feeling, 1 hidden effect (the three large-swing cases);
- 2 perception illusion, 1 true null (the three small-swing cases);
- within each cell, ranked by percentile then disruption; one case per match.
- No case was chosen because it was famous. Netherlands-Sweden,
  Germany-Curacao and Switzerland-Bosnia were the planning-stage favourites;
  they qualify only if the matrix puts them there.

## Reading
- 'Hidden effect' cases are the most important for the video: the break
  visibly flipped the shot balance and no pilot source discussed it. The
  selected one (Panama v England, 2nd break) is stark — Panama went from 1 shot
  to England's 3 before the break, to 6 shots against England's 0 after it, and
  still lost 0-2. A total pressure flip that left no trace in the narrative,
  because the scoreboard never moved.
- The two planning-stage favourites (Germany-Curacao, Netherlands-Sweden) did
  qualify on their own merits — both scored at the 100th percentile. Switzerland-
  Bosnia did not make the cut, which is the matrix doing its job.
- 'Perception illusion' cases carry a public claim while the swing sits inside
  the ordinary range for that same match-half.
- Each case still needs a manual tactical review before it goes in the report;
  the matrix picks WHICH matches to review, not what to conclude.
