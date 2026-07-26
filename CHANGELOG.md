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
