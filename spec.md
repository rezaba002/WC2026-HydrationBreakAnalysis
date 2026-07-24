# WC2026 Hydration Break Analysis — Frozen Analysis Specification

**Frozen:** 2026-07-24 (Milestone 1, before any independent outcome collection)
**Status:** FROZEN. Values may be refined once during the initial audit, before viewing
independent post-break outcomes. Any change must be recorded in `CHANGELOG.md` with a reason.

This document is the human-readable specification. Machine-readable values live in
`config/analysis_spec.yaml`. If they disagree, the YAML is wrong and must be fixed.

---

## 1. Research question

> Did the universal hydration-break policy in the 2026 World Cup measurably change
> attacking performance, and if the average effect was small, why were the breaks
> repeatedly perceived as decisive?

### Frozen thesis (hypothesis, not conclusion)

Hydration breaks had little detectable average effect on attacking momentum, yet they
were repeatedly perceived as decisive and produced measurable structural changes in
coaching opportunities, substitution timing and match duration. The final wording must
follow the evidence.

We are **not** trying to beat the existing preprint (arXiv 2607.19783); its near-zero
average finding is the starting point, not the target.

---

## 2. Units of analysis

### Break level
One row per hydration break. Primary key: `match_id + break_number`.
Expected n ≈ 203 breaks across ≈ 102 matches (verified in Milestone 1).

### Team-break level
Two rows per break, one per team. Primary key: `match_id + break_number + team_id`.
≈ 406 rows.

**Non-negotiable:** ~406 rows are NOT 406 independent observations. The two rows per
break are near-mirror images. The independent interruption units are breaks, nested in
matches. Sample size is always reported in breaks and matches, never as the team-row
count.

### Timeline level
Event/minute-level timeline per match with both clocks (see §4).

---

## 3. Outcome hierarchy

| Tier | Outcomes |
|---|---|
| **Primary** *(amended 2026-07-24, CHANGELOG A2/A3)* | shot difference; shots-on-target difference; balance disruption \|Δ(shots_home − shots_away)\|; P(next shot); P(next goal, sparse) |
| **Secondary** | shot-share change (only where both windows have ≥1 shot, coverage reported); FIFA match-level xG (match totals only); SofaScore Attack Momentum — explicitly labelled secondary AND proprietary |

Per-shot xG is unavailable from the independently auditable layer (FIFA PMSRs
carry team xG totals only); see CHANGELOG A2.

No single black-box momentum index carries the story. Sparse xG does not fully capture
pressure either (most 5-minute windows contain no shots) — the full outcome ladder is
reported.

**Windows:** 5, 8 and 10 break-adjusted minutes; primary window = **8 break-adjusted
minutes** (CHANGELOG A1).

---

## 4. Dual clocks — every central result computed twice

| Clock | Definition |
|---|---|
| **Display clock** | Displayed football minute. The break occupies ~23'–26' of it; clock runs during the break. |
| **Break-adjusted clock** *(renamed 2026-07-24, CHANGELOG A1)* | Hydration-break dead time removed — and ONLY that; throw-ins, VAR, injuries remain. Report as "N displayed minutes excluding the hydration stoppage", never "N minutes of active play". |

A naive 10-before vs 10-after comparison on the match clock gives the "after" side only
~7 minutes of real football. Every headline number is reported under both alignments.
The break-adjusted timeline is a core engineering dependency and must be validated before
the final placebo test.

---

## 5. Placebo design — two tests, two questions

### Test A (primary, causal): randomized pseudo-breaks
For each real break:
1. Enumerate eligible non-break minutes in the same match and half (or equivalent
   historical half).
2. Match ONLY on: half, score state, stage, eligible clock region.
3. Exclude candidate minutes near: goals, penalties, red cards, major VAR
   interruptions, halftime/full time, actual hydration breaks.
4. **Pre-window dominance (xG/shots/pressure) enters as an adjustment covariate,
   NEVER as a matching key.** Matching on unusually high recent dominance rebuilds the
   selection mechanism inside the control group and makes the test circular.
5. Draw ≥ 10,000 pseudo-breaks; compare the observed real-break effect against the
   full null distribution.

Interpretation: "Was the post-break change more unusual than what normally happens
after comparable moments?" — NOT a claim of randomized treatment assignment.

### Test B (secondary, descriptive): state-matched
Matches on pre-window dominance. Answers the narrower, audience-relevant question:
"what normally happens after a period of comparable pressure?" Labelled descriptive.
It is not the causal claim. Reporting both and showing agreement is the goal.

### Fixed placebo minutes (14, 34, 59, 79)
Visualization only. Never the inference.

---

## 6. Uncertainty

- **Primary:** match-level bootstrap — resample entire matches with replacement,
  5,000 iterations, fixed seed.
- **Robustness:** hierarchical model — observations nested in breaks nested in matches.
- Report effect sizes and compatibility intervals, **not p-values**.
- Cluster by match, not by break: two breaks per match plus repeated team observations
  mean break-level clustering understates uncertainty exactly where the design is
  weakest.

---

## 7. Historical baselines

Substitution timing and added time compare against **World Cup 2018 AND World Cup
2022** (optionally Euro 2024 / Copa América 2024 as sensitivity). Qatar 2022 alone is
a bad baseline — anomalously long added time would mask the effect.

Historical event source: StatsBomb Open Data (2018, 2022).

---

## 8. Substitution analysis

Not a raw 2026 histogram. The deliverable is a **difference curve**: 2026 substitution
density minus historical expected density at the same minutes. A narrow excess directly
around the second break supports the tactical-timeout thesis; a broad hump is normal
60–70' behaviour.

Confounds controlled: score state, half, stage, team strength, effective remaining
minutes, minute-recording rounding. Framed as association, not causation.

Metrics: density by minute; first-substitution minute; P(sub within ±3' of second
break); by score state; trailing vs leading; group vs knockout.

---

## 9. Added time and duration

Distinguish: announced added time vs displayed final-whistle minute vs real elapsed
broadcast duration. The ~6 mandated break minutes sit INSIDE the match clock; the
question is whether boards grew beyond that — did breaks displace or stack on other
stoppages?

Measure per match: H1 added time, H2 added time, full-time displayed minute, goals
after 45:00 and after 90:00, proportion of matches exceeding 100 displayed minutes,
stage-specific distributions. Compare 2018 / 2022 / 2026.

---

## 10. Exclusion rules (frozen)

Excluded from treated windows:
- red card in window
- penalty in window
- unresolved break time
- corrupted event timeline

Every exclusion is listed in `data/processed/exclusions.csv` with a reason. Exclusions
are never hidden.

**Coverage target: 102 matches / 203 breaks.** The two missing matches are documented,
not chased. The pipeline stays capable of adding them later.

---

## 11. Perception dataset (preregistered)

**Inclusion rule (frozen before any collection):** include a claim only when a
commentator, manager, player, or major media outlet explicitly attributes a change in a
**specific match** to a **specific hydration break**.

Full codebook: `docs/perception_codebook.md`. Target ≈ 40 usable claims. Rejected
candidates are recorded with reasons. Objective-data evaluation is blinded where
practical. The claim-coding rules are frozen before comparing claims with xG outcomes.

Headline metric: proportion of specific public momentum claims supported by an
objectively unusual post-break change.

---

## 12. Case studies

3 positive + 3 null cases, selected AFTER the quantitative analysis using the
transparent 2×2 matrix (public perception high/low × measurable change high/low).
Planning-stage candidates (Netherlands–Sweden, Germany–Curaçao, Switzerland–Bosnia)
are not guaranteed selections. Null cases are mandatory.

---

## 13. Statistical guardrails (non-negotiable)

- Spec frozen before independent outcome collection.
- Effect sizes + compatibility intervals; no p-value dichotomies.
- Match-level resampling or explicitly nested models.
- Multiple break-adjusted windows (5/8/10).
- Randomized placebo inference; fixed-minute placebos for visuals only.
- Confirmatory and exploratory analyses separated; interactions exploratory unless
  preregistered. The `leadside` breakdown is exploratory: naive cuts largely reproduce
  regression to the mean. If it appears in the video, the caveat appears in the video.
- Association is never interpreted as physiological proof. Player hydration, core
  temperature, injury prevention are OUT of scope for our own measurements.
- FIFA's motive is never inferred from broadcaster monetization. The line:
  "FIFA called them a player-welfare measure. Broadcasters discovered hundreds of
  millions of dollars in new inventory."
- A provider's proprietary momentum index is never described as objective ground truth.
- Exclusions are never hidden.

### Robustness checks
5/8/10-minute windows · H1 vs H2 breaks · group vs knockout · drop red-card windows ·
drop penalty windows · drop goals immediately before break · exact vs nominal break
timing · xG vs shots · leave-one-match-out · match-cluster bootstrap.

---

## 14. Source hierarchy for the independent event layer

1. Official FIFA post-match report PDFs (fifatrainingcentre.com, parsed via
   `wc26-analytics/wc26/fifa_pdf.py` approach)
2. FBref match reports (collection or validation support)
3. Other public match reports for gap filling
4. SofaScore-derived data as sensitivity analysis only

Collection requirements: local caching, rate limiting (~3 s/request on FBref), retry
logic, raw HTML/PDF preservation where permitted, parser tests, manual validation
sample, per-source provenance. Scraped provider data is never redistributed; raw
provider files stay separate from project-generated summaries.

---

## 15. Deferred until all seven core outputs exist

Heat-adequacy chart · France–Iraq missing-break box · broadcast ad-coding sample ·
historical external-control design · full preprint replication · advanced WBGT
reconstruction · large-scale sentiment analysis · physical tracking analysis ·
injury-causation claims · chasing matches 103–104 · additional tournaments.
