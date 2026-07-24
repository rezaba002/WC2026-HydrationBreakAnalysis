# Milestone 1 Report — Source Audit & Master Tables

**Date:** 2026-07-24
**Status:** Complete. All acceptance criteria met. Milestone 2 not started (requires approval).

---

## Work completed

1. **Frozen spec** written before any outcome collection: [spec.md](spec.md) +
   [config/analysis_spec.yaml](config/analysis_spec.yaml).
2. **Three source repos cloned** and pinned (commits in
   [config/sources.yaml](config/sources.yaml)).
3. **Source inventory** with SHA-256, sizes, rows, columns, missingness for 18 files:
   `data/processed/source_inventory.csv` (`python -m src.audit`).
4. **Master tables** built and validated:
   `matches.csv` (104), `venues.csv` (16), `breaks.csv` (203),
   `exclusions.csv` (3), `source_coverage.csv` (104).
5. **Provisional null recalculated** with a match-cluster bootstrap:
   `reports/tables/provisional_null.md`.
6. **Two scripted charts**: `reports/figures/fig_break_timing.png`,
   `reports/figures/fig_wbgt.png`.
7. **Perception dataset preregistered**: frozen codebook
   (`docs/perception_codebook.md`) + empty claim/rejection templates in
   `data/manual/`. No collection has begun.
8. **16 validation tests**, all passing (`python -m pytest tests -q`).

## Actual counts (verified, not assumed)

| quantity | expected | actual |
|---|---|---|
| matches in FIFA backbone | 104 | **104** |
| treated matches | ~102 | **102** (70 group + 32 knockout) |
| treated break events | ~203 | **203** (102 H1 + 101 H2) |
| historical control minutes | ~8,946 | **8,946** (426 matches, 11 competitions) |
| SofaScore↔FIFA id mapping | — | **103/103 mapped, 1:1, zero ambiguity** (no repeated team pairs) |

## Provisional null (audit statistic, NOT a final result)

Momentum drop (pre − post, SofaScore proprietary index):
**treated 7.91** (203 breaks / 102 matches) vs **control 7.11** (8,946 minutes / 426 matches).
Difference **+0.80**, 95% match-cluster bootstrap interval **[−2.11, +3.85]** —
consistent with the handoff's one-line null and with arXiv 2607.19783.

All handoff reference values reproduced exactly: H1/H2 break-minute distributions,
WBGT min/median/max = 17.8 / 26.1 / 37.2 °C, and 87 of 203 breaks above the 28 °C
FIFPRO threshold.

## Discrepancies from repository documentation

1. **Hydration repo README overstates shipped files** (as the handoff warned):
   `wc2026_group_momentum.json`, `wc2026_knockout_raw.json`, `xg_2026.json` are NOT
   standalone files. However, `manifest.json` internally carries fixture/goal/break
   summaries keyed by those filenames — more than the handoff expected.
2. **7 group manifests list their two break bands in reverse order** (H2 first).
   Handled by assigning bands by minute, not list position.
3. **14 of 139 group break bands have corrupt `end` minutes** (zero-length, e.g.
   23→23, or merged spans, e.g. 23→71). Starts are reliable (all 203 agree with
   treated covariates); durations from these bands are nulled and flagged
   `implausible_end` in `breaks.csv`.
4. **FIFA dataset's `kickoff_time_utc` is not consistently UTC** — gaps up to 25 h
   vs SofaScore epoch timestamps. Harmless for the id join (team pairs are unique)
   but SofaScore `ts` should be the authoritative kickoff time for any
   time-of-day analysis (weather join).
5. `match_events.csv` confirmed to contain **zero substitutions** and no shot-level
   data (goals/cards/assists/VAR/shootouts only) — Output 4 cannot come from it.

## Exclusions (`data/processed/exclusions.csv`)

| entity | match | reason |
|---|---|---|
| match | #44 Jordan–Algeria (group) | absent from the hydration repo entirely |
| match | #1 Mexico–South Africa (opener) | manifest entry with both break bands exists, but no treated covariate rows shipped |
| half | #41 France–Iraq H2 | no second-half break in any shipped source (manifest shows one band only, 23'–25'). Internally consistent; **still needs independent external verification** before entering the report |

Coverage 102/104 matches, 203/204 possible break records — matches the frozen
target. Not chasing the gaps; pipeline can absorb them later.

## Missing data / inputs

- `WC2026_104_games_narration.pdf` — not found in Downloads; expected at
  `external/narration/`. Needed only for the video-writing stage.
- StatsBomb open-data (2018/2022) — deliberately deferred to Milestone 2.
- Minute-level momentum / xG arrays — not shipped anywhere; only regenerable via
  SofaScore (`fetch_sofascore.py`) on this machine if we choose to (secondary-tier
  outcome only).

## Generated artifacts

```
data/processed/   source_inventory.csv, matches.csv, venues.csv, breaks.csv,
                  exclusions.csv, source_coverage.csv
data/manual/      perception_claims.csv, perception_rejections.csv  (empty templates)
docs/             perception_codebook.md  (frozen 2026-07-24)
reports/tables/   provisional_null.md, audit_claims.md
reports/figures/  fig_break_timing.png, fig_wbgt.png
tests/            16 tests, all passing
```

## Blockers

None for Milestone 1. For Milestone 2, the following need decisions/inputs:

1. **FIFA post-match PDFs** (fifatrainingcentre.com) — primary independent shot/xG
   source. Reachable from this machine; fetching needs your go-ahead.
2. **FBref scraping** for 2026 substitution minutes — check current terms first;
   3 s rate limit, full local cache.
3. **StatsBomb open-data clone** (~large repo) for 2018/2022 baselines.

## Exact next actions (Milestone 2 — awaiting approval)

1. Clone StatsBomb open data; extract 2018/2022 substitution + event timing tables.
2. Fetch and parse FIFA post-match PDFs (shot-level xG, subs, added time) using the
   `wc26-analytics` parser as a starting point; parser tests + manual validation
   sample per spec §14.
3. Build the dual-clock timeline (`clocks` module) and validate the active-play
   timeline before any placebo work.
4. FBref substitution pull as validation/gap-fill for 2026.
