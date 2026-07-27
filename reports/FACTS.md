# FACT SHEET — every number the prose is allowed to quote

Generated 2026-07-28 by `python -m src.facts` from the tables in
`reports/tables/`. **Do not re-type numbers into prose from anywhere else.**
`tests/test_report_sync.py` fails the build when a document disagrees with this.

## The primary sample

> Primary Test A sample = 183 breaks (8-minute window, maximal clean control support). The cross-window common-support sample = 148 breaks (valid at all of w=3/5/8/10 simultaneously), used only by the exploratory E1 decomposition.

## 1. Test A — primary matched counterfactual (balance disruption, w=8)

| variant | breaks | matches | effect | 95% CI (match-clustered) | excludes 0 |
|---|---|---|---|---|---|
| **PRIMARY — Test A** | 183 | 101 | -0.073 | [-0.258, +0.116] | no |
| ≥3 controls | 152 | 95 | -0.173 | [-0.372, +0.030] | no |
| ≥5 controls | 132 | 86 | -0.196 | [-0.411, +0.022] | no |
| ≥10 controls | 18 | 18 | -0.948 | [-1.486, -0.411] | YES |

Leave-one-match-out range [-0.101, -0.044] across 102 refits.

**Sayable:** no detectable difference from comparable ordinary minutes.
**Not sayable:** robust across all specifications — the support sensitivity drifts to -0.948 on 18 selected breaks.

## 2. The clock artifact

| clock | w | observed P(shot) | null |
|---|---|---|---|
| display | 5 | 0.405 | 0.617 |
| display | 8 | 0.689 | 0.787 |
| display | 10 | 0.811 | 0.838 |
| adjusted | 5 | 0.682 | 0.617 |
| adjusted | 8 | 0.818 | 0.787 |
| adjusted | 10 | 0.858 | 0.838 |

Headline contrast at w=8: display **0.689** vs break-adjusted **0.818** against a null of 0.787.

## 3. Test B — directional (did the attacking side lose its edge?)

| w | breaks | matches | swing real | swing matched | D | 95% CI |
|---|---|---|---|---|---|---|
| 5 | 88 | 67 | -1.091 | -0.955 | -0.136 | [-0.501, +0.247] |
| 8 | 63 | 55 | -1.032 | -0.781 | -0.251 | [-0.775, +0.235] |
| 10 | 33 | 30 | -1.121 | -1.379 | +0.258 | [-0.558, +1.034] |

**Every Test B interval includes zero.**

## 4. E1 — clock decomposition (EXPLORATORY, common support 148 breaks / 92 matches)

| w | D | 95% CI | A (real − synthetic) | 95% CI |
|---|---|---|---|---|
| 3 | +0.019 | [-0.043, +0.084] | +0.011 | [-0.034, +0.054] |
| 5 | +0.023 | [-0.034, +0.081] | +0.010 | [-0.034, +0.053] |
| 8 | +0.057 | [+0.001, +0.113] | +0.044 | [-0.005, +0.095] |
| 10 | +0.061 | [-0.002, +0.126] | +0.057 | [+0.003, +0.113] |

**1 of 4 E1 D intervals exclude zero** ([+0.001, +0.113]); the remainder include it.
 
**1 of 4 E1 A intervals exclude zero** ([+0.003, +0.113]); the remainder include it.

## 5. Perception

- Stratified random sweep: claims on **4 of 48 sampled breaks** (8.3%, 95% CI 3.3–19.6%).
- Unique claimed breaks supported: **7/12 (58%)** — the citable rate.
- Claim level: 8/16 (50%).
- 22 claims collected, 19 source-verified, on 15 of 203 breaks.

## 6. Substitutions

- Within ±3' of the own-match break: **154/825 = 18.7%** of H2 subs.
- Minute-matched expectation: 19.6% (2018), 20.7% (2022) — so 2026 is BELOW, not above.
- Displacement: 6.8% in the 3' before the stoppage, 15.0% in the 3' from the restart.

## 7. Commercial inventory (arithmetic only — no motive claim)

- Recorded: 580 min ≈ 9.7 hours across 203 breaks (5.7 min per match).
- Guaranteed by policy: 208 slots ≈ 10.4 hours tournament-wide.

## 8. Appendix — yellow cards (weak proxy, not tempo)

| w | breaks | D | 95% CI |
|---|---|---|---|
| 5 | 194 | -0.0035 | [-0.0210, +0.0141] |
| 8 | 183 | -0.0054 | [-0.0234, +0.0120] |
| 10 | 148 | -0.0039 | [-0.0226, +0.0145] |

**Every card interval includes zero.**

