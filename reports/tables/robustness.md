# Robustness pass — placebo analysis (spec §13)

Window 8 break-adjusted minutes, seed 20260724, 10000 draws.
`pct` = share of null draws at or above the observed mean; ~0.5 means
real breaks look like ordinary matched minutes.

## 1. THE DECISIVE TEST — placement matching

Pseudo-breaks restricted to ±5' of each real break's own minute,
so real and pseudo are compared at the same point of the match.

| variant | n | observed | null | null 95% | pct |
|---|---|---|---|---|---|
| signed shot diff — unmatched (main run) | 196 | +0.403 | -0.152 | [-0.403, +0.097] | 0.000 |
| signed shot diff — PLACEMENT MATCHED | 158 | +0.316 | -0.136 | [-0.228, -0.044] | 0.000 |
| balance disruption — unmatched | 196 | +1.556 | +1.640 | [+1.480, +1.801] | 0.850 |
| balance disruption — PLACEMENT MATCHED | 158 | +1.456 | +1.649 | [+1.570, +1.728] | 1.000 |

### 1b. Symmetric event screening (the asymmetry the diagnostic exposed)

Pseudo candidates were always screened for proximity to goals / red cards /
VAR; real breaks were not. Real breaks could therefore sit right after a goal
and capture the conceding team's surge, which their controls exclude by
construction. Here the SAME screen is applied to real breaks.

| variant | n | observed | null | null 95% | pct |
|---|---|---|---|---|---|
| signed shot diff — symmetric screen | 173 | +0.335 | -0.096 | [-0.364, +0.173] | 0.001 |
| signed shot diff — symmetric screen + placement matched | 155 | +0.290 | -0.158 | [-0.252, -0.065] | 0.000 |
| balance disruption — symmetric screen + placement matched | 155 | +1.439 | +1.649 | [+1.568, +1.729] | 1.000 |

## 2. Subgroups (primary metric: balance disruption, placement matched)

| subgroup | n | observed | null | null 95% | pct |
|---|---|---|---|---|---|
| first-half breaks | 84 | +1.095 | +1.589 | [+1.500, +1.679] | 1.000 |
| second-half breaks | 74 | +1.865 | +1.716 | [+1.595, +1.838] | 0.014 |
| group stage | 107 | +1.458 | +1.711 | [+1.607, +1.813] | 1.000 |
| knockout stage | 51 | +1.451 | +1.520 | [+1.392, +1.647] | 0.885 |

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
| drop windows containing a red card | 158 | +1.456 | +1.649 | [+1.570, +1.728] | 1.000 |
| drop breaks with a goal in the 3' before | 156 | +1.442 | +1.664 | [+1.583, +1.744] | 1.000 |
| nominal 22'/67' timing instead of actual | 173 | +1.549 | +1.608 | [+1.503, +1.711] | 0.884 |

## 4. Leave-one-match-out (primary metric, placement matched)

Full sample gap (observed − null): **-0.193**.
Leave-one-match-out range: **[-0.224, -0.158]** across 102 refits.
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
