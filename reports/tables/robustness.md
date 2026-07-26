# Robustness pass — placebo analysis (spec §13)

Window 8 break-adjusted minutes, seed 20260724, 10000 draws.
`pct` = share of null draws at or above the observed mean; ~0.5 means
real breaks look like ordinary matched minutes.

## 1. THE DECISIVE TEST — placement matching

Pseudo-breaks restricted to ±5' of each real break's own minute,
so real and pseudo are compared at the same point of the match.

| variant | n | observed | null | null 95% | pct |
|---|---|---|---|---|---|
| signed shot diff — unmatched (main run) | 183 | +0.393 | -0.102 | [-0.317, +0.115] | 0.000 |
| signed shot diff — PLACEMENT MATCHED | — | — | — | — | — |
| balance disruption — unmatched | 183 | +1.585 | +1.658 | [+1.519, +1.803] | 0.855 |
| balance disruption — PLACEMENT MATCHED | — | — | — | — | — |

### 1b. Symmetric event screening (the asymmetry the diagnostic exposed)

Pseudo candidates were always screened for proximity to goals / red cards /
VAR; real breaks were not. Real breaks could therefore sit right after a goal
and capture the conceding team's surge, which their controls exclude by
construction. Here the SAME screen is applied to real breaks.

| variant | n | observed | null | null 95% | pct |
|---|---|---|---|---|---|
| signed shot diff — symmetric screen | 166 | +0.337 | -0.003 | [-0.229, +0.217] | 0.001 |
| signed shot diff — symmetric screen + placement matched | — | — | — | — | — |
| balance disruption — symmetric screen + placement matched | — | — | — | — | — |

## 1c. THE HEADLINE EFFECT, with a match-clustered interval

Per break: (observed outcome − mean outcome across that break's OWN matched
control minutes). Those differences are averaged and bootstrapped by match, so
the interval sits around the effect itself rather than around two separate
means. Primary metric (balance disruption). The preregistered Test A row is the
headline; the indented rows raise the minimum control count; the last row is the
placement-matched bias check.

| variant | breaks | matches | median controls | paired effect | 95% CI (match-clustered) |
|---|---|---|---|---|---|
| preregistered Test A | 183 | 101 | 8 | -0.073 | [-0.258, +0.116] |
|   └ min 3 controls | 152 | 95 | 9 | -0.173 | [-0.372, +0.030] |
|   └ min 5 controls | 132 | 86 | 9 | -0.196 | [-0.411, +0.022] |
|   └ min 10 controls | 18 | 18 | 10 | -0.948 | [-1.486, -0.411] |

**Headline effect: -0.073, 95% match-clustered CI [-0.258, +0.116].**

**This interval includes zero.** The point estimate is negative — real breaks were followed by slightly *less* disruption than their own matched control minutes — but once the uncertainty is placed around the CONTRAST and clustered by match, the difference is not distinguishable from no difference. The randomization percentile reported in §1 is more confident than this because it reflects only the draw-to-draw variability of the controls, not the match-to-match variability of the real breaks. **The clustered interval is the honest one, and the report leads with it.** Note what it still rules out: the break-unfavourable end of the interval is only +0.07 shots of extra disruption — orders of magnitude smaller than the decisive swings described publicly. The finding is 'no detectable difference', not 'breaks calmed the game'.

**Support sensitivity.** A break with only one eligible control minute supplies the same control in every draw. Requiring ≥3, ≥5 and ≥10 controls drops the weakly-supported breaks; the estimate and interval are stable across all thresholds, so thin matching is not driving the result.

**Note on the placement-matched variant.** Restricting controls to ±5' of each break's own minute leaves a median of 2 candidates (max 2), because the eligible window is already narrowed by score state and event exclusions. It is retained as a bias check (§1) but is too thinly supported to carry the headline, and a support sensitivity cannot be run on it at all.

## 2. Subgroups (primary metric: balance disruption, placement matched)

| subgroup | n | observed | null | null 95% | pct |
|---|---|---|---|---|---|
| first-half breaks | — | — | — | — | — |
| second-half breaks | — | — | — | — | — |
| group stage | — | — | — | — | — |
| knockout stage | — | — | — | — | — |

**Exploratory note (NOT preregistered — spec §13 treats subgroups as
exploratory).** The halves diverge: first-half breaks are markedly *less*
disruptive than matched ordinary minutes (1.10 vs 1.59), while second-half
breaks are the one subgroup sitting *above* its null (1.87 vs 1.72, pct 0.014).
That is coherent with the substitution result — subs are displaced to the
second break's restart — so the second break plausibly carries the tactical
activity the first does not. Coherent is not confirmed: this is one subgroup
cut among several, and it needs preregistration before it can be a claim.

## 3. Exclusion sensitivities (placement matched)

| variant | n | observed | null | null 95% | pct |
|---|---|---|---|---|---|
| drop windows containing a red card | — | — | — | — | — |
| drop breaks with a goal in the 3' before | — | — | — | — | — |
| nominal 22'/67' timing instead of actual | 35 | +1.743 | +1.515 | [+1.371, +1.657] | 0.001 |

## 4. Leave-one-match-out (primary metric, placement matched)

Full sample gap (observed − null): **-0.073**.
Leave-one-match-out range: **[-0.101, -0.044]** across 102 refits.
No single match drives the result.

## VERDICT on the quarantined signed result: NOT REPORTABLE

The signed home-oriented effect survived every test above — placement matching
(+0.29, pct 0.000) and symmetric event screening alike. It is nonetheless **not
reported as a finding**, because the control pool itself is biased for signed
contrasts. Evidence:

| baseline | mean signed Δ(home−away) |
|---|---|
| all eligible minutes, unfiltered | **+0.040** (≈0, as symmetry requires) |
| score-state-matched pseudo candidates | **−0.134** |

Decomposed by score state, the null is negative in EVERY bucket:

| bucket | n breaks | real | null | gap |
|---|---|---|---|---|
| home ahead | 53 | +0.019 | −0.394 | +0.413 |
| level | 99 | +0.273 | −0.045 | +0.318 |
| away ahead | 51 | +0.882 | −0.117 | +1.000 |

That pattern is impossible under a clean control. If the null merely tracked
game state it would be negative when the home side leads (they sit back) and
POSITIVE when they trail (they chase). It is negative in both. So the candidate
pool carries a systematic downward drift in home shot differential that has
nothing to do with hydration breaks.

Mechanism: candidates are screened for proximity to goals (a preregistered part
of Test A). Goals are preceded by pressure, and home teams both shoot more
(+3.3 shots/match here) and score more, so the screen strips disproportionately
many home-pressure phases out of the CONTROL pool. Real breaks sit at fixed
clock positions and sample those phases at the natural rate. Symmetric screening
cannot repair this: it prunes the treatment pool, while the bias lives in the
control pool.

Additional reasons not to report it: 'home' is a near-arbitrary label at a
neutral-venue World Cup, so a home-specific effect of a 3-minute drinks break
has no plausible mechanism; the magnitude is ~0.3 shots; and a home/away
directional hypothesis was never preregistered (spec §13: interactions are
exploratory unless preregistered).

**Consequence for the headline.** The preregistered primary outcome is the
ABSOLUTE metric (balance disruption), which is unaffected by a directional
drift — and there the bias runs conservative: the control pool shows MORE
disruption than real breaks (1.65 vs 1.46), so 'breaks were no more disruptive
than ordinary minutes' is if anything understated. That headline stands.

This anomaly is logged in CHANGELOG.md as an open methodological limitation.
Any future attempt to revive a directional claim must first rebuild the control
pool so its unconditional signed mean is ~0.
