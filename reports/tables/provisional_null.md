# Provisional null — audit recalculation (NOT a final result)

Source: shipped `treated_covariates.json` / `control_candidates_all.json` only.
Outcome: SofaScore momentum summaries (proprietary, secondary-tier). 
Bootstrap: match-cluster, 5000 iterations, seed 20260724.

## Momentum drop (pre_level − post_level)

| group | n obs | n matches | mean pre | mean post | mean drop |
|---|---|---|---|---|---|
| treated breaks | 203 | 102 | 13.5 | 5.6 | 7.91 |
| control minutes | 8946 | 426 | 10.6 | 3.5 | 7.11 |

**Difference (treated − control): +0.80**, 95% match-cluster bootstrap interval [-2.11, +3.85].

Momentum drops sharply after real breaks — and almost as sharply after comparable non-break minutes selected the same way. The visible-in-one-line null: high momentum reverts regardless of whether anyone stops the game.

## Reference-value verification (handoff §6)

- H1 break minutes: {22: 5, 23: 51, 24: 21, 25: 16, 26: 4, 27: 3, 29: 1, 30: 1}
  - matches handoff reference: True
- H2 break minutes: {67: 11, 68: 41, 69: 32, 70: 7, 71: 4, 72: 3, 73: 2, 75: 1}
  - matches handoff reference: True
- Handoff reference drops: treated 7.9, control 7.1 (recomputed: 7.9, 7.1)
- WBGT across breaks: min 17.8, median 26.1, max 37.2 (reference: 17.8 / 26.1 / 37.2)
- Breaks above 28°C FIFPRO threshold: 87 of 203 (reference: 87)

## Caveats

- Proprietary black-box index; primary outcomes for the project are xG/shots from the independent event layer (Milestone 2).
- Control minutes come from 11 historical competitions, not from WC2026 itself; the frozen design's randomized within-match pseudo-breaks (Test A) supersede this comparison.
- The `leadside` breakdown is exploratory and largely reflects regression to the mean; it is intentionally not reported here.
