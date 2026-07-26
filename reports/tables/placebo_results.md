# Randomized placebo analysis (Test A) — Core Output 3

Breaks analysed: 148 of 203 (55 skipped, no eligible score-state-matched candidate minutes: [(5, 'H1'), (6, 'H1'), (9, 'H1'), (12, 'H2'), (16, 'H2'), (17, 'H2'), (19, 'H1'), (19, 'H2'), (20, 'H1'), (22, 'H1'), (27, 'H1'), (29, 'H1'), (33, 'H2'), (35, 'H1'), (35, 'H2'), (38, 'H2'), (39, 'H1'), (40, 'H1'), (40, 'H2'), (42, 'H2'), (45, 'H1'), (49, 'H2'), (50, 'H2'), (54, 'H1'), (55, 'H1'), (58, 'H2'), (59, 'H2'), (60, 'H2'), (62, 'H1'), (66, 'H2'), (67, 'H1'), (67, 'H2'), (68, 'H2'), (70, 'H1'), (70, 'H2'), (71, 'H2'), (74, 'H2'), (79, 'H1'), (81, 'H1'), (83, 'H2'), (84, 'H2'), (86, 'H1'), (86, 'H2'), (88, 'H1'), (89, 'H2'), (92, 'H2'), (94, 'H2'), (95, 'H1'), (95, 'H2'), (100, 'H1'), (100, 'H2'), (101, 'H1'), (101, 'H2'), (103, 'H1'), (103, 'H2')])
Candidates per break: median 5, min 1, max 12
Draws: 10000, seed 20260724. Bootstrap: match-cluster, 5000.

Outcome definitions per CHANGELOG A2/A3. next_goal omitted here: goal events
are too sparse per window; reported in the robustness pass instead.

| clock | W | outcome | observed mean | null mean | null 2.5-97.5% | pct of null ≥ obs | boot 95% CI |
|---|---|---|---|---|---|---|---|
| adjusted | 5 | total_change | +0.101 | -0.049 | [-0.216, +0.122] | 0.043 | [-0.150, +0.331] |
| adjusted | 5 | shot_diff_change | +0.236 | +0.076 | [-0.115, +0.270] | 0.053 | [-0.026, +0.486] |
| adjusted | 5 | balance_disruption | +1.304 | +1.208 | [+1.081, +1.331] | 0.071 | [+1.134, +1.483] |
| adjusted | 5 | sot_diff_change | +0.081 | +0.032 | [-0.061, +0.135] | 0.187 | [-0.049, +0.207] |
| adjusted | 5 | next_shot_within_w | +0.682 | +0.617 | [+0.568, +0.662] | 0.006 | [+0.603, +0.759] |
| adjusted | 8 | total_change | +0.236 | -0.281 | [-0.459, -0.108] | 0.000 | [-0.062, +0.545] |
| adjusted | 8 | shot_diff_change | +0.426 | +0.001 | [-0.203, +0.209] | 0.000 | [+0.126, +0.733] |
| adjusted | 8 | balance_disruption | +1.480 | +1.681 | [+1.534, +1.824] | 0.997 | [+1.279, +1.692] |
| adjusted | 8 | sot_diff_change | +0.088 | -0.013 | [-0.115, +0.088] | 0.028 | [-0.070, +0.248] |
| adjusted | 8 | next_shot_within_w | +0.818 | +0.787 | [+0.750, +0.818] | 0.058 | [+0.753, +0.875] |
| adjusted | 10 | total_change | +0.142 | -0.470 | [-0.642, -0.297] | 0.000 | [-0.236, +0.542] |
| adjusted | 10 | shot_diff_change | +0.318 | -0.063 | [-0.257, +0.135] | 0.000 | [-0.070, +0.678] |
| adjusted | 10 | balance_disruption | +1.764 | +1.925 | [+1.784, +2.068] | 0.988 | [+1.543, +1.987] |
| adjusted | 10 | sot_diff_change | +0.020 | -0.053 | [-0.142, +0.041] | 0.079 | [-0.171, +0.203] |
| adjusted | 10 | next_shot_within_w | +0.858 | +0.838 | [+0.811, +0.865] | 0.130 | [+0.805, +0.907] |
| display | 5 | total_change | -0.581 | -0.048 | [-0.216, +0.115] | 1.000 | [-0.770, -0.397] |
| display | 5 | shot_diff_change | +0.081 | +0.077 | [-0.108, +0.270] | 0.491 | [-0.152, +0.309] |
| display | 5 | balance_disruption | +1.014 | +1.209 | [+1.088, +1.331] | 1.000 | [+0.853, +1.181] |
| display | 5 | sot_diff_change | +0.000 | +0.032 | [-0.068, +0.135] | 0.754 | [-0.115, +0.113] |
| display | 5 | next_shot_within_w | +0.405 | +0.617 | [+0.568, +0.662] | 1.000 | [+0.320, +0.487] |
| display | 8 | total_change | -0.466 | -0.280 | [-0.453, -0.101] | 0.984 | [-0.732, -0.201] |
| display | 8 | shot_diff_change | +0.223 | +0.001 | [-0.203, +0.209] | 0.020 | [-0.079, +0.532] |
| display | 8 | balance_disruption | +1.480 | +1.679 | [+1.534, +1.824] | 0.996 | [+1.273, +1.691] |
| display | 8 | sot_diff_change | +0.047 | -0.014 | [-0.115, +0.088] | 0.125 | [-0.103, +0.192] |
| display | 8 | next_shot_within_w | +0.689 | +0.787 | [+0.750, +0.818] | 1.000 | [+0.610, +0.766] |
| display | 10 | total_change | -0.500 | -0.467 | [-0.635, -0.297] | 0.658 | [-0.822, -0.168] |
| display | 10 | shot_diff_change | +0.189 | -0.060 | [-0.250, +0.128] | 0.007 | [-0.175, +0.543] |
| display | 10 | balance_disruption | +1.649 | +1.923 | [+1.777, +2.068] | 1.000 | [+1.451, +1.853] |
| display | 10 | sot_diff_change | +0.020 | -0.052 | [-0.142, +0.047] | 0.081 | [-0.148, +0.189] |
| display | 10 | next_shot_within_w | +0.811 | +0.838 | [+0.811, +0.865] | 0.977 | [+0.745, +0.875] |

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
