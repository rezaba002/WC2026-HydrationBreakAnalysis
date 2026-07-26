# Test B — did the attacking team lose its advantage? (PREREGISTERED, spec §5)

Test A and the E1 clock analysis measure TOTAL activity, which can stay flat while momentum changes hands. This is the directional test the spec reserved for that question, and the one the public claim actually makes.

The attacking side is fixed from the PRE-window only (shots on target, ties on total shots) and then frozen. `swing` = post-break advantage − pre-break advantage; negative means the attacking side lost its edge. Post-break windows start at resumption.

**Controls are state-matched:** ordinary minutes in the same match and half, same score state, whose OWN pre-window advantage EQUALS the break's, oriented by their own pre-window leader. Without that, regression to the mean alone guarantees a negative swing and the test would be meaningless.

## Did the attacking team lose more advantage than usual?

| w | breaks | matches | mean pre-break advantage | swing (real) | swing (matched spells) | **D** | 95% CI |
|---|---|---|---|---|---|---|---|
| 5 | 88 | 67 | +1.25 | -1.091 | -0.955 | **-0.136** | [-0.501, +0.247] |
| 8 | 63 | 55 | +1.30 | -1.032 | -0.781 | **-0.251** | [-0.775, +0.235] |
| 10 | 33 | 30 | +1.70 | -1.121 | -1.379 | **+0.258** | [-0.558, +1.034] |

**Coverage warning.** Requiring controls whose whole window clears the real break (the contamination fix) cut this sample hard: 88 / 63 / 33 breaks at 5 / 8 / 10 minutes, against 94 / 91 / 90 before. At w=10 only ~30 matches remain and the interval is correspondingly wide — that row should be read as underpowered rather than as an independent confirmation.

Note how large the *unadjusted* swings are in BOTH columns: teams that have just been dominating give most of that edge back within minutes, break or no break. That is regression to the mean, and it is exactly what an unmatched analysis would have mistaken for a break effect.

**Weighting.** Every break contributes equally: each is differenced against the MEAN of its own control pool, and D is the mean of those paired differences. Pooling all candidates instead would let a break with 15 eligible controls outweigh one with a single control by 15x on the control side while counting once on the real side — the point estimate and the interval would then describe different estimands.

## Shots on target, and momentum changing hands

| w | SOT swing D | 95% CI | reversal rate (real) | reversal (matched) | **D** | 95% CI |
|---|---|---|---|---|---|---|
| 5 | -0.040 | [-0.252, +0.184] | 23.9% | 27.9% | **-4.1%** | [-15.0%, +7.0%] |
| 8 | +0.054 | [-0.280, +0.361] | 27.0% | 26.5% | **+0.5%** | [-13.4%, +14.9%] |
| 10 | -0.081 | [-0.561, +0.387] | 18.2% | 35.9% | **-17.7%** | [-38.2%, +3.8%] |

`reversal` = the previously attacking team is behind on shots in the post window — momentum has changed hands.

## Coverage and exclusions

| w | analysed | directionally ambiguous | no state-matched control | median controls |
|---|---|---|---|---|
| 5 | 88 | 76 | 39 | 4 |
| 8 | 63 | 69 | 71 | 3 |
| 10 | 33 | 71 | 99 | 2 |

Ambiguous = neither side led the pre-window on shots on target or total shots (including genuinely quiet pre-windows). Those breaks are counted and excluded; they are never re-oriented using post-break information.

## Limits

- Descriptive, not causal. The spec labels Test B descriptive: matching on pre-window dominance rebuilds part of the selection mechanism, which is why Test A (not this) carries the causal claim.
- Exact matching on integer pre-window advantage keeps the comparison clean but thins the control pool; breaks with no matched control are reported above and excluded rather than matched loosely.
- Shots and shots on target only. No per-shot xG exists in the auditable layer (CHANGELOG A2), so 'advantage' is a count, not a chance-quality measure.
- CHANGELOG A5 ruled the HOME-oriented signed contrast unreportable because the control pool's unconditional home−away mean is biased. Orientation here is by pre-window dominance, not home/away, and both arms are oriented by the same rule, so that specific bias should cancel — the home/away split below is the check on whether it does.

### Sensitivity — matching on (shot advantage, SOT advantage)

The attacking side is chosen on shots on target first, but the main matching key is the total-shot advantage alone, so two spells can pair while differing in SOT dominance. Requiring both to match tests whether 'comparable pressure' means more than the same raw shot differential. It costs coverage.

| w | breaks (main) | breaks (strict) | D (main) | D (strict) | 95% CI (strict) |
|---|---|---|---|---|---|
| 5 | 88 | 63 | -0.136 | +0.115 | [-0.302, +0.566] |
| 8 | 63 | 39 | -0.251 | -0.308 | [-0.884, +0.263] |
| 10 | 33 | 19 | +0.258 | -0.004 | [-1.118, +1.035] |

### A5 diagnostic — attacker home vs away (orientation-stratified)

Each break is compared with ONLY its same-orientation controls (home-attacking breaks against home-attacking control spells, likewise away), one value per break; breaks with no same-orientation control are dropped rather than pooled. An earlier version differenced both strata against the POOLED control mean, which confounded control-pool composition with the effect.

| w | D, attacker home | D, attacker away | gap | breaks (home / away) |
|---|---|---|---|---|
| 5 | -0.125 | -0.190 | +0.065 | 36 / 28 |
| 8 | -1.059 | -0.135 | -0.924 | 26 / 19 |
| 10 | -1.104 | -0.685 | -0.419 | 12 / 9 |

The gap is small and **changes sign across windows**, which is what noise looks like rather than a systematic orientation bias. An earlier, candidate-weighted version of this table showed a large and consistently positive gap (+0.63 / +0.43 / +0.58); that was an artefact of the weighting defect described above, and it disappeared once every break was given equal weight against its own same-orientation controls.

The strata are still **not reported as findings**: they are the signed, home-oriented class CHANGELOG A5 quarantined, and each cell holds only ~30–45 breaks. They serve here purely as a check that the pooled estimate is not an average of two large opposing biases — and it is not.
