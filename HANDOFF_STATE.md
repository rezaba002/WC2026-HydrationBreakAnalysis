# Development history (archived)

> **This file is historical and no longer describes the current state of the project.**
> It previously served as a working handoff between development sessions. It is retained
> only as a record that the work proceeded in gated milestones.
>
> For the current state, use:
> - **[README.md](README.md)** — findings, outputs, reproduction
> - **[reports/final/REPORT.md](reports/final/REPORT.md)** — the full analysis and conclusions
> - **[CHANGELOG.md](CHANGELOG.md)** — every specification amendment and limitation (A1–A5)
> - **[spec.md](spec.md)** — the frozen analysis specification
> - **[reports/tables/](reports/tables/)** — generated result tables

## How the project was built

The work ran in gated phases, each requiring sign-off before the next began — the
mechanism that kept scope from drifting:

1. **Milestone 1 — audit and master tables.** Source inventory with SHA-256 hashes,
   `matches` / `breaks` / `venues` / `exclusions` / coverage tables, verification of the
   104 / 102 / 203 / 8,946 counts, and an independent recomputation of the provisional
   momentum null. See `MILESTONE_1_REPORT.md`.
2. **Milestone 2 — independent event layer.** FIFA post-match reports parsed into shots,
   substitutions and per-player physical data; StatsBomb 2018/2022 baselines; the
   dual-clock module.
3. **Milestone 3 — analysis.** Randomized placebo (Core Output 3) and its robustness pass,
   substitution timing (4), perception dataset (5), added time (6), case studies (7), plus
   the fresh-legs and late-game extensions.
4. **Publication.** Report, PDF, references, licensing, CI.

## Decisions worth preserving

- The analysis specification was frozen **before** any outcome was computed; all later
  changes are dated in `CHANGELOG.md`.
- A strong, robustness-passing **directional result was found and then deleted** once its
  control pool proved biased for signed contrasts (CHANGELOG A5).
- The perception sample was drawn at random and **pre-specified**, so the denominator is
  unbiased; null results are logged in `data/manual/perception_sweep_log.csv`.
- Every perception quote was re-read against its source; three failed and are excluded.
- Case studies are selected by a transparent 2×2 matrix, never by fame — one case changed
  cells when the systematic sweep ran, and the change is documented rather than absorbed.

## Source quirks (still useful to anyone re-deriving the data)

1. The hydration repo's README overstates what it ships; `manifest.json` carries the
   summaries keyed by the missing filenames.
2. Seven group manifests list break bands in reverse order — assign by minute, not
   position.
3. Fourteen group bands have corrupt `end` minutes; durations are nulled and flagged.
4. The FIFA dataset's `kickoff_time_utc` is not reliably UTC; SofaScore timestamps are
   authoritative.
5. FIFA's official match numbering differs from the dataset's date-ordered `match_id` —
   join by team-code pair.
6. PMSR outcome "On Target - Goal Prevented" is a save, not a goal.
7. Own goals never appear in the scorer's PMSR shot log; per-team reconciliation infers
   them (goals reconcile 104/104).
8. PMSR physical pages emit `sprints` and `top_speed` out of order in ~150 rows; detected
   and corrected in the parser.
9. The PMSR shot log's row order is not chronological — periods are assigned by minute.
10. FBref/Sports-Reference blocks automated access; it was not scraped.
