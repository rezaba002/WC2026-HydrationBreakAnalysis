# Test B — did the attacking team lose its advantage? (PREREGISTERED, spec §5)

Test A and the E1 clock analysis measure TOTAL activity, which can stay flat while momentum changes hands. This is the directional test the spec reserved for that question, and the one the public claim actually makes.

The attacking side is fixed from the PRE-window only (shots on target, ties on total shots) and then frozen. `swing` = post-break advantage − pre-break advantage; negative means the attacking side lost its edge. Post-break windows start at resumption.

**Controls are state-matched:** ordinary minutes in the same match and half, same score state, whose OWN pre-window advantage EQUALS the break's, oriented by their own pre-window leader. Without that, regression to the mean alone guarantees a negative swing and the test would be meaningless.

## Did the attacking team lose more advantage than usual?

| w | breaks | matches | mean pre-break advantage | swing (real) | swing (matched spells) | **D** | 95% CI |
|---|---|---|---|---|---|---|---|
| 5 | 94 | 70 | +1.26 | -1.043 | -1.023 | **-0.020** | [-0.372, +0.327] |
| 8 | 91 | 76 | +1.37 | -1.165 | -1.028 | **-0.136** | [-0.538, +0.263] |
| 10 | 90 | 72 | +1.66 | -1.311 | -1.214 | **-0.097** | [-0.550, +0.333] |

Note how large the *unadjusted* swings are in BOTH columns: teams that have just been dominating give most of that edge back within minutes, break or no break. That is regression to the mean, and it is exactly what an unmatched analysis would have mistaken for a break effect.

**Weighting.** Every break contributes equally: each is differenced against the MEAN of its own control pool, and D is the mean of those paired differences. Pooling all candidates instead would let a break with 15 eligible controls outweigh one with a single control by 15x on the control side while counting once on the real side — the point estimate and the interval would then describe different estimands.

## Shots on target, and momentum changing hands

| w | SOT swing D | 95% CI | reversal rate (real) | reversal (matched) | **D** | 95% CI |
|---|---|---|---|---|---|---|
| 5 | +0.041 | [-0.157, +0.234] | 23.4% | 29.2% | **-5.8%** | [-15.9%, +4.9%] |
| 8 | +0.054 | [-0.209, +0.312] | 29.7% | 28.8% | **+0.9%** | [-11.0%, +12.7%] |
| 10 | -0.100 | [-0.344, +0.148] | 30.0% | 31.5% | **-1.5%** | [-14.3%, +10.7%] |

`reversal` = the previously attacking team is behind on shots in the post window — momentum has changed hands.

## Coverage and exclusions

| w | analysed | directionally ambiguous | no state-matched control | median controls |
|---|---|---|---|---|
| 5 | 94 | 76 | 33 | 4 |
| 8 | 91 | 69 | 43 | 4 |
| 10 | 90 | 71 | 42 | 3 |

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
| 5 | 94 | 70 | -0.020 | +0.185 | [-0.217, +0.611] |
| 8 | 91 | 64 | -0.136 | -0.193 | [-0.674, +0.297] |
| 10 | 90 | 69 | -0.097 | -0.009 | [-0.504, +0.481] |

### A5 diagnostic — attacker home vs away (orientation-stratified)

Each break is compared with ONLY its same-orientation controls (home-attacking breaks against home-attacking control spells, likewise away), one value per break; breaks with no same-orientation control are dropped rather than pooled. An earlier version differenced both strata against the POOLED control mean, which confounded control-pool composition with the effect.

| w | D, attacker home | D, attacker away | gap | breaks (home / away) |
|---|---|---|---|---|
| 5 | +0.015 | -0.140 | +0.155 | 40 / 33 |
| 8 | -0.283 | -0.078 | -0.206 | 39 / 31 |
| 10 | -0.098 | -0.115 | +0.017 | 45 / 29 |

The gap is small and **changes sign across windows**, which is what noise looks like rather than a systematic orientation bias. An earlier, candidate-weighted version of this table showed a large and consistently positive gap (+0.63 / +0.43 / +0.58); that was an artefact of the weighting defect described above, and it disappeared once every break was given equal weight against its own same-orientation controls.

The strata are still **not reported as findings**: they are the signed, home-oriented class CHANGELOG A5 quarantined, and each cell holds only ~30–45 breaks. They serve here purely as a check that the pooled estimate is not an average of two large opposing biases — and it is not.
