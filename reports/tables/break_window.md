# Display-clock artefact: window decomposition (EXPLORATORY)

**Post hoc, not preregistered** — motivated by the momentum-graphic
discussion; results were seen before the plan was fixed. Logged as CHANGELOG E1.

Common-support sample: breaks valid at all windows (196 breaks / 102 matches of 203/102).
Rates are shots per minute, both teams. Every dead-time prediction uses each
break's OWN measured duration, never a fixed three minutes.

| w | pre | N (from call) | dead-time prediction | C (from resumption) | control | **D = C − control** | 95% CI (match-clustered) |
|---|---|---|---|---|---|---|---|
| 3 | 0.207 | -0.196 | -0.198 | +0.010 | -0.000 | **+0.011** | [-0.070, +0.089] |
| 5 | 0.231 | -0.135 | -0.132 | +0.004 | +0.001 | **+0.003** | [-0.059, +0.069] |
| 8 | 0.217 | -0.064 | -0.077 | +0.025 | -0.005 | **+0.029** | [-0.023, +0.082] |
| 10 | 0.226 | -0.057 | -0.064 | +0.013 | -0.008 | **+0.021** | [-0.031, +0.063] |

### Transition-minute sensitivity

Break bands are recorded to whole minutes, so for shorter breaks play restarts
part-way through the minute at `restart`. That minute is a TRANSITION bin and may
contain residual dead time. Repeating D with the post-window starting one minute
later measures how much that matters instead of asserting it:

| w | D (post-window from restart) | D (post-window from restart + 1) | 95% CI |
|---|---|---|---|
| 3 | +0.011 | **+0.057** | [-0.029, +0.139] |
| 5 | +0.003 | **+0.015** | [-0.048, +0.080] |
| 8 | +0.029 | **+0.038** | [-0.013, +0.091] |
| 10 | +0.021 | **+0.035** | [-0.016, +0.077] |

Excluding the transition minute shifted the adjusted estimates upward by an average of 0.020 shots per minute, without changing the overall conclusion — every interval still includes zero. Including the partially observed transition minute therefore appears to attenuate the estimates downward. No clustered interval was computed for the DIFFERENCE between the two specifications, so this is described as an apparent shift rather than a quantified bias.

`N` is what a display-clock window reports. `D` is the estimate that matters:
post-resumption change, differenced against matched ordinary minutes.

## Validation 1 — synthetic dead time

Take ordinary matched control minutes — normal passages of football — and
insert each break's OWN observed duration into the clock as artificial dead
time. Nothing is deleted from the pre-window and no quiet periods are selected;
only elapsed display-clock time is inserted. If the collapse reappears there,
the measurement procedure produces it, not hydration breaks.

The formal test is the **direct paired contrast** A = (real, from call) −
(synthetic stoppage), bootstrapped by match with the matched control minute
redrawn inside every iteration. Comparing one point estimate against the other's
interval would not be a test.

| w | real N (from call) | synthetic stoppage | **A = real − synthetic** | 95% CI (match-clustered) |
|---|---|---|---|---|
| 3 | -0.196 | -0.206 | **+0.010** | [-0.034, +0.069] |
| 5 | -0.135 | -0.124 | **-0.011** | [-0.054, +0.042] |
| 8 | -0.064 | -0.082 | **+0.018** | [-0.028, +0.069] |
| 10 | -0.057 | -0.070 | **+0.013** | [-0.032, +0.055] |

**All A intervals include zero.** The decline measured from the break call did not differ detectably from the decline produced by inserting an equivalent synthetic stoppage at matched ordinary minutes — i.e. the apparent collapse is closely reproduced by the measurement procedure alone.

Note on wording: those control minutes are ordinary passages of football. The procedure inserts artificial dead time into them; it does not select quiet periods.

### Sensitivity — measured durations only

Duration drives the synthetic stoppage, and 76 of the 196 analysed breaks have a median-imputed duration. Repeating the placebo on the breaks whose duration was actually measured:

| w | n breaks | real N | synthetic | A = real − synthetic | 95% CI |
|---|---|---|---|---|---|
| 3 | 120 | -0.186 | -0.208 | +0.022 | [-0.039, +0.092] |
| 5 | 120 | -0.133 | -0.126 | -0.008 | [-0.066, +0.062] |
| 8 | 120 | -0.068 | -0.085 | +0.018 | [-0.037, +0.084] |
| 10 | 120 | -0.067 | -0.073 | +0.006 | [-0.048, +0.068] |

## Validation 2 — duration dose-response (UNDERPOWERED, inconclusive)

If the clock drives it, the naive decline should steepen as dead share grows,
while the resumption-aligned change should be flat. **Our data cannot really
test this.** Measured durations take only three values (2 / 3 / 4 min), 78 of
203 are imputed at the median and are excluded here, and at w=3 the dead share
is constant. What remains is a 2-vs-3-vs-4 contrast — directionally consistent
but far too thin to call a validation. Reported for completeness, not as
evidence.

| w | slope of N on dead share | slope of C on dead share | distinct shares | n measured |
|---|---|---|---|---|
| 3 | -0.165 | +0.057 | 2 | 120 |
| 5 | -0.162 | -0.036 | 3 | 120 |
| 8 | -0.085 | +0.110 | 3 | 120 |
| 10 | -0.097 | +0.334 | 3 | 120 |

## Interpretation limits

- All A intervals include zero; they exclude differences larger than about 0.07 shots/min between the real and synthetic declines. Whether that is 'small' is a judgement about football, not a statistical fact.
- The D estimates permit modest effects in either direction, especially at the 3-minute window. This is 'no detectable decline', NOT proof of no effect.
- Shot activity is not the momentum algorithm. This shows how a display-clock window can manufacture an apparent collapse; it does not reproduce, and cannot prove the cause of, any published momentum curve.
- Activity in the final minute before the call is lower than at control minutes. That pre-trend may reflect stoppage selection, timestamp granularity or random variation and is NOT interpreted causally here.
- **Alignment is to an ESTIMATED resumption minute, not the exact restart instant.** Break bands are whole minutes and no restart timestamp exists in any source we hold, so the minute at `restart` is a transition bin that may contain residual dead time. It is excluded from interpretation, and its effect is measured in the sensitivity above rather than asserted.
- Event-study bands are POINTWISE 95% intervals at each relative minute. They are descriptive; they are not simultaneous bands, and the trajectory as a whole has not been subjected to a joint test. Formal inference is the window contrasts.
