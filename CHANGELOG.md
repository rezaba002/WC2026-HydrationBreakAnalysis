# Specification changelog

Amendments to the frozen spec. Permitted only while no post-break outcome has been
viewed (spec header rule); each entry is dated and states its reason.

## 2026-07-24 — pre-analysis amendments (no post-break outcomes viewed yet)

**A1 — Clock renamed: `active_play_clock` → `break_adjusted_clock`.**
The second clock removes hydration-break dead time only — not throw-ins, VAR,
injuries or celebrations. The old name overclaimed. Behaviour unchanged; all
user-facing wording updated. Report phrasing: "N displayed minutes excluding the
hydration stoppage", never "N minutes of active play".

**A2 — Shots-based outcomes promoted to primary.**
Per-shot xG is unavailable from the independently auditable FIFA layer (PMSRs
carry team-level xG only; FBref blocks tooling and was not scraped). Primary
confirmatory outcomes are now: shot difference, shots-on-target difference,
P(next shot), P(next goal, labelled sparse). SofaScore momentum stays
secondary/proprietary; FIFA match-level xG validates match totals only.

**A3 — Balance-disruption outcome defined (before computing any outcome).**
Primary disruption metric is count-based and always defined:
`|Δ(shots_home − shots_away)|` between pre and post windows. Share-based
versions (`|Δ shot share|`) are secondary, computed only where both windows
contain ≥1 shot, with coverage reported. Rationale: share is 0/0-undefined in
quiet windows; dropping them would rebuild selection-on-activity.

## 2026-07-26 — terminology, deviation and control-definition corrections

**A6 — "Causal" removed; hierarchical-model deviation recorded.**
The spec headed Test A "primary, causal" while also stating it does not identify a
randomized treatment effect, and the report's limitations said everything is
associational. Those cannot all hold. Treatment was never randomly assigned, so
Test A is now described throughout as the **primary matched counterfactual
analysis**: it tests whether post-break football was unusual relative to eligible
pseudo-break moments. "causal inference" also removed from CITATION.cff keywords.
Separately, the spec promised a hierarchical nested model as robustness; it was not
implemented. Match-clustered bootstrapping is used throughout instead, alongside
placement matching, exclusion sensitivities, subgroup cuts and leave-one-match-out.
Recorded as a deviation rather than dropped silently.

**A7 — Control windows must not overlap the real break.**
`eligible_minutes()` excluded only candidate ANCHOR minutes near the break band, never
checking that the candidate's pre/post WINDOWS clear it. Measured contamination of the
control arm: 12.2% of controls at w=5, **46.8% at the primary w=8**, and 67.7% at w=10
contained the actual hydration break. Controls described as "ordinary uninterrupted
football" therefore contained the treatment, biasing every contrast toward the null —
the direction of all headline findings. Fixed centrally: a candidate survives only if
its whole `[c-w, c+w)` span clears the band plus a one-minute transition washout. All
callers pass their window; a regression test asserts no control window can overlap a
break. Coverage fell as a result (E1 203→148 breaks; Test B 94/91/90→88/63/33) and
placement matching became largely infeasible, since an anchor within 5' of a break
cannot have an 8' window clear of it. All affected analyses were rerun; conclusions
survive, with the changed numbers and reduced power reported in place.

## 2026-07-27 — deviation record and reporting-integrity consolidation (v2.0.0)

**A8 — Substitution confound adjustment specified but NOT implemented.**
Spec §8 says the substitution comparison controls for "score state, half, stage, team
strength, effective remaining minutes, minute-recording rounding". Only minute matching
and stage/half stratification were implemented; score state and team strength are
reported DESCRIPTIVELY (shares by score state) and never adjusted for. The headline
substitution result is a minute-matched share contrast, not a covariate-adjusted one.
Recorded as a deviation rather than quietly dropped. It does not threaten the finding's
direction — 2026 sits *below* both historical expectations, and an unadjusted comparison
would if anything favour the excess the thesis predicted — but the result should be read
as a raw minute-matched contrast.

**A9 — Placement matching retired to a reported coverage failure.**
After A7, a control anchor within ±5' of a break cannot have an 8' window clear of it, so
the placement-matched variant returns nothing. It had still been used to LABEL the
subgroup, exclusion-sensitivity and leave-one-match-out sections, which either printed
empty tables under a "placement matched" heading or (in the leave-one-out case) ran the
unmatched specification under a matched label. Those three sections now run and are
labelled as the **primary unmatched specification**; §1 retains the placement-matched rows
as explicitly empty, with the reason stated. No estimate changed meaning; several tables
that had been blank since A7 are populated again.

**Reporting integrity — generated facts replace hand-typed numbers.**
The recurring defect in this project was never the analysis; it was that corrected numbers
did not propagate into prose. Five review rounds each found stale figures (clock
probabilities, an obsolete robustness summary, wrong perception denominators) and false
universal claims ("every interval includes zero") sitting beside tables that disproved
them. Fixed structurally rather than by re-checking:

- `src/facts.py` regenerates every headline number into `reports/facts.json` and
  `reports/FACTS.md` from the analysis tables. Prose quotes that file; nothing else.
- `util.interval_sentence()` GENERATES interval-summary sentences by counting, so a
  universal claim cannot survive a rerun that falsifies it. `break_window.py` and
  `cards.py` now use it.
- `tests/test_report_sync.py` fails the build when README or the report disagrees with
  the computed values, when a generated table universalises a false interval claim, when
  a document claims robustness the sensitivity analysis contradicts, or when the checks
  themselves stop matching enough of a document to be meaningful.

**Primary sample declared once.** Primary Test A = **183 breaks** (8-minute window,
maximal clean control support). The cross-window common-support sample = **148 breaks**
(valid at w=3/5/8/10 simultaneously), used only by E1. The second is a subset of the
first, not a correction to it; both are labelled everywhere they appear.

**Version.** Released as **2.0.0**. The public history had already reached v1.4.1, and a
subsequent `v1.2.0-final` tag moved the version backwards — an error. The major bump
reflects the A7 control-definition change, which altered samples and estimates repo-wide.

## 2026-07-26 — exploratory addition (does NOT alter the confirmatory design)

**E1 — Exploratory clock-artefact event study.** After completion of the
preregistered primary analysis and review of external momentum research, we added
a post hoc analysis of shot activity around hydration breaks. It compares windows
measured from the break call with windows measured from play resumption, and with
equivalent synthetic stoppages inserted at matched ordinary periods. Window
lengths (3/5/8/10 min), common-support rules, match-clustered bootstrap
procedures and sensitivity analyses were fixed before final figure production.

**This analysis is explanatory and was not part of the preregistered confirmatory
design.** It was conceived *after* the primary results had been seen, so it cannot
be presented as preregistered, and it changes no primary outcome, no exclusion
rule and no headline number. Its purpose is narrow: to separate display-clock
measurement from post-resumption play.

*Corrections applied to the first prototype before anything was reported:*
- each break's OWN measured duration is used, replacing a fixed three minutes;
- the direct break-versus-control contrast (D) is estimated, replacing separate
  intervals on the two component means;
- the matched control minute is redrawn INSIDE every clustered bootstrap draw, so
  matching and match-level uncertainty both propagate;
- a synthetic-stoppage placebo was added, and the formal test is the direct paired
  contrast (A = real − synthetic), not a point estimate compared with another
  estimate's interval;
- the duration dose-response was restricted to measured durations and is reported
  as **underpowered and inconclusive** (only 2/3/4-minute values exist, 78 of 203
  imputed);
- a positional-indexing defect that mapped control pools to breaks by a modulo
  expression was fixed and is now covered by regression tests;
- **breaks without at least one eligible matched-control minute were excluded,
  matching the primary placebo analysis.** An earlier draft substituted a
  zero-valued control for those seven breaks, which would have analysed 203
  breaks instead of 196. The analysed sample is 196 breaks / 102 matches, and
  the measured-duration sensitivity 120 breaks. A regression test now asserts
  that support membership equals window validity AND real control availability;
- the minute-before-the-call dip is recorded but explicitly NOT interpreted.

**A5 — Signed/directional placebo outcomes ruled NOT REPORTABLE (2026-07-25,
after the robustness pass; a limitation, not a spec change).**
The control pool built by preregistered Test A rules is biased for SIGNED,
team-oriented contrasts: its unconditional signed mean is −0.13 where an unbiased
control must sit at ~0 (all unfiltered eligible minutes give +0.04), and it is
negative in all three score-state buckets, which is impossible if it merely
tracked game state. Cause: the preregistered goal-proximity screen strips
disproportionately many home-pressure phases from the CONTROL pool, while real
breaks sample them at the natural rate. The apparent home-team gain therefore
does not survive scrutiny despite passing placement matching and symmetric
screening, and is excluded from the report, video and article. The preregistered
PRIMARY outcome is absolute (balance disruption) and is unaffected in direction;
there the bias is conservative. Reviving any directional claim requires first
rebuilding the control pool to an unconditional signed mean of ~0.
Full evidence: `reports/tables/robustness.md` §1b and Verdict.

**A4 — Perception collection staged.**
Pilot of 15–20 claims to assess source availability and coding consistency,
then continue toward ~40. The frozen inclusion rule and codebook are unchanged.
