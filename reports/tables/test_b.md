# Test B — did the attacking team lose its advantage? (PREREGISTERED, spec §5)

Test A and the E1 clock analysis measure TOTAL activity, which can stay flat while momentum changes hands. This is the directional test the spec reserved for that question, and the one the public claim actually makes.

The attacking side is fixed from the PRE-window only (shots on target, ties on total shots) and then frozen. `swing` = post-break advantage − pre-break advantage; negative means the attacking side lost its edge. Post-break windows start at resumption.

**Controls are state-matched:** ordinary minutes in the same match and half, same score state, whose OWN pre-window advantage EQUALS the break's, oriented by their own pre-window leader. Without that, regression to the mean alone guarantees a negative swing and the test would be meaningless.

## Did the attacking team lose more advantage than usual?

| w | breaks | matches | mean pre-break advantage | swing (real) | swing (matched spells) | **D** | 95% CI | D, orientation-standardised |
|---|---|---|---|---|---|---|---|---|
| 5 | 94 | 70 | +1.26 | -1.043 | -1.034 | **-0.009** | [-0.413, +0.372] | -0.005 |
| 8 | 91 | 76 | +1.37 | -1.165 | -1.060 | **-0.104** | [-0.580, +0.300] | -0.069 |
| 10 | 90 | 72 | +1.66 | -1.311 | -1.276 | **-0.036** | [-0.571, +0.356] | -0.034 |

Note how large the *unadjusted* swings are in BOTH columns: teams that have just been dominating give most of that edge back within minutes, break or no break. That is regression to the mean, and it is exactly what an unmatched analysis would have mistaken for a break effect.

The final column standardises the control pool to the treated sample's home/away composition, because the two pools differ by 3–11 percentage points on which side was attacking (see the A5 diagnostic). It moves the estimate negligibly relative to the interval width, so composition mismatch is not driving the result.

## Shots on target, and momentum changing hands

| w | SOT swing D | 95% CI | reversal rate (real) | reversal (matched) | **D** | 95% CI |
|---|---|---|---|---|---|---|
| 5 | -0.011 | [-0.174, +0.267] | 23.4% | 32.2% | **-8.8%** | [-17.5%, +6.4%] |
| 8 | +0.049 | [-0.223, +0.323] | 29.7% | 30.9% | **-1.2%** | [-12.2%, +14.1%] |
| 10 | -0.087 | [-0.363, +0.176] | 30.0% | 35.5% | **-5.5%** | [-14.3%, +12.0%] |

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

### A5 diagnostic — attacker home vs away (orientation-stratified)

Each stratum is compared with controls of the SAME orientation (home-attacking breaks against home-attacking control spells, and likewise away). An earlier version of this diagnostic differenced both strata against the POOLED control mean, which confounded control-pool composition with the effect and produced a spurious home/away gap.

| w | D, attacker home | D, attacker away | gap | control n (home / away) |
|---|---|---|---|---|
| 5 | +0.296 | -0.332 | +0.628 | 229 / 187 |
| 8 | +0.150 | -0.283 | +0.433 | 249 / 165 |
| 10 | +0.217 | -0.361 | +0.578 | 207 / 145 |

**The gap does not vanish, so the A5 bias survives into this design, and the home/away strata above are therefore NOT REPORTABLE as findings** — they are exactly the class of signed, home-oriented contrast that CHANGELOG A5 quarantined. They are shown only as a diagnostic on the pooled estimate.

What the pooled estimate inherits from that bias is limited to composition: the treated and control pools differ by 3–11 points on which side was attacking. Standardising the controls to the treated composition (final column of the main table) shifts the estimate far less than the interval width, so the headline survives. Anyone wishing to interpret the home/away split itself must first rebuild the control pool as A5 requires.
