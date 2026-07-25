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
