# Randomized placebo analysis (Test A) — Core Output 3

Breaks analysed: 196 of 203 (7 skipped, no eligible score-state-matched candidate minutes: [(6, 'H1'), (29, 'H1'), (38, 'H2'), (67, 'H1'), (70, 'H2'), (79, 'H1'), (100, 'H2')])
Candidates per break: median 13, min 1, max 19
Draws: 10000, seed 20260724. Bootstrap: match-cluster, 5000.

Outcome definitions per CHANGELOG A2/A3. next_goal omitted here: goal events
are too sparse per window; reported in the robustness pass instead.

| clock | W | outcome | observed mean | null mean | null 2.5-97.5% | pct of null ≥ obs | boot 95% CI |
|---|---|---|---|---|---|---|---|
| adjusted | 5 | total_change | +0.020 | +0.000 | [-0.184, +0.189] | 0.424 | [-0.188, +0.221] |
| adjusted | 5 | shot_diff_change | +0.265 | -0.087 | [-0.296, +0.117] | 0.001 | [+0.016, +0.510] |
| adjusted | 5 | balance_disruption | +1.347 | +1.219 | [+1.087, +1.352] | 0.033 | [+1.173, +1.531] |
| adjusted | 5 | sot_diff_change | +0.092 | -0.022 | [-0.122, +0.077] | 0.016 | [-0.030, +0.208] |
| adjusted | 5 | next_shot_within_w | +0.648 | +0.655 | [+0.597, +0.709] | 0.629 | [+0.579, +0.714] |
| adjusted | 8 | total_change | +0.199 | -0.064 | [-0.291, +0.158] | 0.011 | [-0.046, +0.439] |
| adjusted | 8 | shot_diff_change | +0.403 | -0.152 | [-0.408, +0.102] | 0.000 | [+0.111, +0.692] |
| adjusted | 8 | balance_disruption | +1.556 | +1.641 | [+1.485, +1.801] | 0.856 | [+1.383, +1.735] |
| adjusted | 8 | sot_diff_change | +0.097 | -0.064 | [-0.184, +0.051] | 0.004 | [-0.046, +0.236] |
| adjusted | 8 | next_shot_within_w | +0.806 | +0.822 | [+0.781, +0.862] | 0.804 | [+0.754, +0.857] |
| adjusted | 10 | total_change | +0.133 | -0.108 | [-0.352, +0.138] | 0.029 | [-0.162, +0.435] |
| adjusted | 10 | shot_diff_change | +0.316 | -0.139 | [-0.413, +0.138] | 0.001 | [-0.026, +0.658] |
| adjusted | 10 | balance_disruption | +1.765 | +1.865 | [+1.694, +2.036] | 0.883 | [+1.567, +1.970] |
| adjusted | 10 | sot_diff_change | +0.061 | -0.056 | [-0.189, +0.071] | 0.042 | [-0.105, +0.227] |
| adjusted | 10 | next_shot_within_w | +0.857 | +0.886 | [+0.852, +0.918] | 0.965 | [+0.812, +0.900] |
| display | 5 | total_change | -0.673 | -0.001 | [-0.184, +0.184] | 1.000 | [-0.829, -0.518] |
| display | 5 | shot_diff_change | +0.061 | -0.086 | [-0.291, +0.117] | 0.084 | [-0.144, +0.273] |
| display | 5 | balance_disruption | +1.031 | +1.219 | [+1.082, +1.357] | 0.998 | [+0.896, +1.174] |
| display | 5 | sot_diff_change | +0.010 | -0.023 | [-0.122, +0.077] | 0.277 | [-0.091, +0.116] |
| display | 5 | next_shot_within_w | +0.378 | +0.654 | [+0.597, +0.709] | 1.000 | [+0.310, +0.447] |
| display | 8 | total_change | -0.515 | -0.041 | [-0.265, +0.184] | 1.000 | [-0.749, -0.294] |
| display | 8 | shot_diff_change | +0.270 | -0.168 | [-0.408, +0.066] | 0.000 | [-0.011, +0.582] |
| display | 8 | balance_disruption | +1.536 | +1.598 | [+1.444, +1.760] | 0.789 | [+1.348, +1.737] |
| display | 8 | sot_diff_change | +0.082 | -0.077 | [-0.189, +0.036] | 0.003 | [-0.051, +0.217] |
| display | 8 | next_shot_within_w | +0.658 | +0.797 | [+0.755, +0.837] | 1.000 | [+0.591, +0.727] |
| display | 10 | total_change | -0.566 | -0.048 | [-0.291, +0.189] | 1.000 | [-0.832, -0.307] |
| display | 10 | shot_diff_change | +0.199 | -0.162 | [-0.418, +0.092] | 0.002 | [-0.126, +0.536] |
| display | 10 | balance_disruption | +1.679 | +1.781 | [+1.617, +1.949] | 0.893 | [+1.497, +1.883] |
| display | 10 | sot_diff_change | +0.031 | -0.074 | [-0.194, +0.046] | 0.047 | [-0.131, +0.185] |
| display | 10 | next_shot_within_w | +0.801 | +0.853 | [+0.816, +0.888] | 0.999 | [+0.745, +0.853] |

## Reading guide
- `pct of null ≥ obs` near 0.5 ⇒ real breaks look like ordinary matched minutes.
- `balance_disruption` is the primary metric (absolute change in shot balance).
- The display clock shows the naive dead-time artefact the video will explain:
  its post window contains ~3 fewer minutes of football after real breaks.
- Windows are break-adjusted display minutes excluding the hydration stoppage
  only (CHANGELOG A1); pseudo-break windows stretch over real bands the same way.

## Placement caveats (documented, not corrected post hoc)
This run implements frozen Test A exactly (match on half / score state / stage /
clock region). Two structural asymmetries remain and are handled in the
planned robustness pass, NOT by editing this confirmatory run:
1. **Post-window displacement.** A real break's post window starts ~3 display
   minutes later than a same-minute pseudo's, so it samples slightly later
   football. Within-half shot rates rise with the clock, which can inflate
   positive `total_change`/`shot_diff_change` after real breaks.
2. **Candidate-minute distribution.** Real breaks cluster at 23'/68'; eligible
   candidates span the whole clock region. Signed outcomes (notably the
   home-shift in `shot_diff_change`) must not be interpreted until the
   robustness pass adds placement-minute adjustment (hierarchical model with
   minute covariate, per spec §6 robustness).
The primary absolute metric and the next-shot probability are far less exposed
to both asymmetries, and both sit at/below the null.
