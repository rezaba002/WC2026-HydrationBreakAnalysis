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

## Why this is the weakest design in the project

The on-screen momentum index is what most viewers actually watched, so it deserves a direct answer. But it can only carry a WEAKER design than the shot-based results, for reasons that are properties of the data rather than choices:

1. **No 2026 control minutes exist.** All 8,946 controls come from 11 OTHER competitions (2018-2025). The randomized within-match pseudo-break design used for shots (Test A) therefore CANNOT be built for momentum — there is nothing within 2026 to draw controls from. This is an external-control comparison across different tournaments, squads and rules eras.
2. **No minute-level momentum series is shipped.** Only pre-level, pre-slope and post-level at each break survive; the underlying curves were stripped from the source repository to avoid redistributing a proprietary index. Rebuilding them would mean re-fetching from the provider.
3. **The index is a proprietary black box.** Its construction is unpublished, so it cannot be audited, and the spec keeps it strictly secondary (CHANGELOG A2).

## What it nevertheless shows: triangulation

Despite the weaker design and a completely different data provider, the momentum index points the same way as the shot analysis: **+0.80** with a 95% match-clustered interval of **[-2.11, +3.85]**, straddling zero. Momentum collapses after breaks — and collapses almost as hard after ordinary comparable minutes.

Two independent measurement systems, two different control strategies, the same null. That agreement is worth more than either result alone, and it is why this weak-design comparison is reported at all.

## Caveats

- Proprietary black-box index; the project's primary outcomes are shot-based, from the independently auditable FIFA layer.
- External controls (see above) — corroboration, never the headline.
- The `leadside` breakdown is exploratory and largely reflects regression to the mean; it is intentionally not reported here.
