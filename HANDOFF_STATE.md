# WC2026 Hydration Break Analysis — Project State Handoff

**Written:** 2026-07-24, after Milestone 1 (complete) and the Milestone 2 data layer (complete).
**Repo:** https://github.com/rezaba002/WC2026-HydrationBreakAnalysis (private; account `rezaba002`)
**Local path:** `E:\1x\Bet\wc2026-hydration-impact\`
**Original design docs:** `C:\Users\baghe\Downloads\HANDOFF.md` and `WC2026_Hydration_Break_Research_HANDOFF_README.md` — the design they froze is unchanged.

This file is the continuation point. A fresh session should read this, `spec.md`, and `MILESTONE_1_REPORT.md`, then continue at §7 below. **Do not re-litigate the design. Do not add analytical branches.**

---

## 1. Project identity

Deliverables: reproducible analysis + comprehensive report + charts + 6–7 min SportOnTheLine video, **plus (added by user): a publishable article and/or rich LinkedIn post** — publication formats derived from the same analysis at the end, not new analysis.

Frozen thesis: hydration breaks had little detectable average effect on attacking momentum, yet were perceived as decisive and produced measurable structural changes (coaching opportunities, substitution timing, match duration). Wording follows the evidence.

**User's stated emphasis (2026-07-24):** pinpoint (a) the physical-strength angle and (b) the coach analysis & talk impact.
- Coach impact → Outputs 4 (subs) + 7 (case studies) + perception mechanism codes. Fully in scope; the data layer below was built for it.
- Physical → FIFA PMSR per-player physical data (discovered this session — see §4) enables match-level physical/fresh-legs analysis. Per-window physiology and injury/core-temperature claims remain **out of scope** per spec §13. WBGT context charts exist.

## 2. Milestone status

| milestone | status |
|---|---|
| M1 — source audit, master tables, provisional null, 2 charts, perception preregistration, tests | ✅ complete (commit `de41875`), see `MILESTONE_1_REPORT.md` |
| M2 data layer — StatsBomb 2018/22, FIFA PDFs fetched+parsed, dual clocks | ✅ complete (commit `3dce7c3`) |
| M3 placebo (Core Output 3) — confirmatory Test A run, results + central chart | ✅ complete (`reports/tables/placebo_results.md`, CHANGELOG A1–A4) |
| M3 substitution timing (Core Output 4) | ✅ complete (`subs_timing.md`, `fig_subs_curve.png`) |
| M3 fresh-legs physical (user emphasis) | ✅ complete (`physical_freshlegs.md`, `fig_freshlegs.png`) |
| M3 late-game proxy (physical-sustain question) | ✅ complete (`late_game.md`, `fig_late_game.png`) |
| M3 added time (Core Output 6) | ✅ complete (`added_time.md`, `fig_added_time.png`) |
| M3 perception pilot (Core Output 5) | ✅ pilot complete, 13 claims (`perception.md`); full ~40 sweep outstanding |
| M3 case studies (Core Output 7) | ✅ selection + graphics (`case_studies.md`, `fig_case_studies.png`); manual tactical review outstanding |
| **All 7 core outputs have results.** Remaining: report, video script, article/LinkedIn | ⏳ not started |
| Case studies, report, video script, article/LinkedIn | ⏳ not started |

## 3. Data assets (`data/processed/`)

| file | rows | content |
|---|---|---|
| `matches.csv` | 104 | FIFA backbone + venue geo + sofascore_id (103 mapped 1:1) + treated flags |
| `venues.csv` | 16 | lat/lon/elevation |
| `breaks.csv` | 203 | break level: start minute (all sources agree), bands, WBGT, tempC, Elo, score state, momentum pre/post |
| `break_bands.csv` | 203 | adjudicated (start, duration, source); 78 durations imputed at median 3.0 |
| `exclusions.csv` | 3 | see §5 |
| `source_coverage.csv` | 104 | per-match field availability by source |
| `source_inventory.csv` | 18 | SHA-256, rows, cols, missingness of external inputs |
| `shots_2026.csv` | 2,554 | FIFA PMSR shot log: minute, period, player, team, outcome, body part, delivery. **No per-shot xG** |
| `substitutions_2026.csv` | 1,914 | on/off rows: minute, player, team, source (pdf_marker / lineup_derived / late / unarbitrated) |
| `physical_2026.csv` | 3,073 | per player-match: total distance, 5 speed zones, high-speed runs, sprints, top speed |
| `fifa_team_stats_2026.csv` | 104 | PMSR team stats incl. match xG (validation layer) |
| `parse_qa.csv` | 104 | per-match parse QA + flags |
| `historical_subs.csv` | 969 | WC2018 (382, 3-sub era) + WC2022 (587, 5-sub era) with score state |
| `historical_match_times.csv` | 128 | half end minutes (added time), ET flags |
| `historical_goals.csv` | 393 | incl. own goals, per period |

`data/manual/`: empty preregistered perception templates. Codebook frozen at `docs/perception_codebook.md` — **collection has not begun; the inclusion rule may not change.**

Raw (local only, gitignored): `data/raw/fifa_pdfs/` — 104 PDFs, 572 MB, hashes in `index.csv`. `external/`: three cloned repos + StatsBomb partial clone (commits pinned in `config/sources.yaml`).

## 4. Key verified numbers

- 104 matches / 102 treated / 203 breaks (102 H1 + 101 H2) / 8,946 control minutes / 11 competitions — all handoff claims confirmed against files.
- Provisional null (audit stat, proprietary momentum index): treated drop **7.91** vs control **7.11** → diff **+0.80**, 95% match-cluster bootstrap CI **[−2.11, +3.85]**. Consistent with arXiv 2607.19783.
- Break starts cluster 23'/68' (nominal 22'/67'). WBGT min/med/max 17.8/26.1/37.2; **87/203 breaks above 28°C** → 116 would not have happened under the old heat rule.
- Added-time baseline: H2 ended ~**94.7'** (2018) vs ~**97.0'** (2022). 2026 comparison still to be computed (KO manifest has `injury`/`periods`; group matches need another source — open item).
- Subs in 60–75': **36.1%** (2018) vs **40.7%** (2022) — baseline for the second-break clustering test.
- FIFA PMSR discovery: 52-page reports with per-shot logs, substitution markers, **per-player physical data** (distance, 5 speed zones, sprints, top speed) — not known to the original handoff.

## 5. Exclusions & source-quirk ledger (hard-won; do not rediscover)

**Exclusions** (`exclusions.csv`): match 44 Jordan–Algeria (absent from hydration repo); match 1 Mexico–South Africa (manifest yes, covariates no); match 41 France–Iraq **H2** (no second-half break in any shipped source — internally consistent, still needs independent external verification before the report).

**Quirks:**
1. Hydration repo README overstates shipped files; `manifest.json` internally carries the summaries keyed by the missing filenames.
2. 7 group manifests list break bands in reverse order → assign by minute, not position.
3. 14/139 group bands have corrupt `end` minutes → durations nulled, flagged `implausible_end`.
4. FIFA dataset `kickoff_time_utc` is NOT reliably UTC (up to 25 h off) → SofaScore `ts` is authoritative.
5. FIFA **official** match numbers ≠ dataset date-ordered `match_id` → join by team-code pair (unique; verified).
6. PMSR team naming: "Korea Republic" ↔ dataset "South Korea" (only variant).
7. PMSR outcome "On Target - Goal Prevented" is a save, NOT a goal; `is_goal` = outcome endswith "- Goal".
8. Own goals never appear in the scorer's PMSR shot log → per-team reconciliation infers them (goals reconcile 104/104).
9. Match 90 (Canada–Morocco) dataset lineup minutes corrupt → marker-only fallback (`pdf_marker_unarbitrated`).
10. Red-carded players are not subbed off; stoppage-time subs are rounded away by lineup minutes (recovered from ≥85' markers).
11. PMSR physical pages omit a few short-cameo players → `physical_rows − 22` is soft QA only, not a subs count validator.
12. wc26-analytics repo numbers are internally inconsistent — used its parser IDEA only; everything re-derived.
13. Team-name map hydration→FIFA: Bosnia & Herzegovina / DR Congo / Iran variants (see `src/util.py`).
14. FBref/Sports-Reference 403-blocks non-browser tooling → NOT scraped; revisit only with user approval if per-shot xG becomes indispensable.
15. **No per-shot xG exists in the layer.** Primary outcomes lean on shots / SOT / P(next shot) — spec's outcome ladder anticipated this; SofaScore-derived xG stays labelled-secondary.

## 6. How to reproduce

```powershell
pip install -r requirements.txt          # Python 3.11
python -m src.audit                      # inventory + claims check
python -m src.build_tables               # master tables
python -m src.provisional_null           # audit null
python -m src.charts                     # fig_break_timing, fig_wbgt
python -m src.statsbomb_extract          # historical baselines
python -m src.fetch_fifa_pdfs            # cached; --discover-only to skip downloads
python -m src.parse_fifa_pdfs            # shots/subs/physical/stats + QA
python -m src.clocks                     # break_bands.csv
python -m pytest tests -q                # 25 tests
```

## 7. Exact next actions (in order)

1. ~~Randomized placebo analysis~~ ✅ DONE (`src/placebo.py`, seed 20260724, 196/203
   breaks, median 13 candidates). Headline: balance disruption 1.556 observed vs
   1.641 null (below-typical); naive display clock shows P(next shot) 0.658 vs
   0.797 null — the dead-time illusion, erased on the break-adjusted clock (0.806
   vs 0.822). Chart: `reports/figures/fig_placebo.png`. Signed home-shift result
   flagged: do NOT interpret before the robustness pass adds placement-minute
   adjustment (see caveats in `placebo_results.md`). Robustness pass still to do:
   H1/H2 and stage cuts, exclusion sensitivities, next-goal, hierarchical model.
2. ~~Substitution difference curve~~ ✅ DONE. Subs did NOT multiply at the break —
   they **moved to the restart**: deficit in the 3' before the stoppage, surplus in
   the 3' after (15.0% vs 12.6%/14.6% historical). ±3' share 18.7% is at/below the
   minute-matched historical expectation, i.e. displacement not creation.
3. ~~Added time~~ ✅ DONE (Core Output 6). 2018 +4.7' vs 2022 +7.1' exact; 2026 board
   minutes unobtainable — reported as last-shot floor only. No late-scoring trend.
4. ~~Fresh-legs physical~~ ✅ DONE. Subs run far hotter than the starters they replace
   (66 vs 46 sprints/90); entry timing barely matters. Deployment story, not physiology.
   Also: `late_game.py` answers the sustain question via a behavioral proxy — final-15'
   shot share is flat across all three cups (17.0/16.8/17.1%).
5. ~~Perception pilot~~ ✅ DONE, 13 claims / 11 breaks; 6 of 11 testable supported.
   **Outstanding: the systematic per-match sweep** (codebook §4 requires iterating all
   104 matches; the pilot was topical). Also outstanding: manual verbatim confirmation
   of all 13 quotes against source URLs — currently `fetch_extracted`, NOT publishable.
6. ~~Case-study 2×2~~ ✅ DONE. Selected: Germany-Curaçao b1 + Netherlands-Sweden b1
   (confirmed feeling), **Panama-England b2 (hidden effect — Panama 1→6 shots, England
   3→0, still lost 0-2)**, Austria-Jordan b2 + England-Congo b1 (perception illusion),
   South Korea-Czechia b2 (true null). Manual tactical review of each still to do.

### Now next
7. **Robustness pass on the placebo** (deferred from step 1): placement-minute
   adjustment before ANY signed/directional result is reported; H1-vs-H2, group-vs-KO,
   drop red-card/penalty windows, leave-one-match-out, next-goal outcome.
8. **Report → video script → article/LinkedIn**, in that order.

## 8. Open decisions for the user

- Repo is **private**; flip to public when ready to publish (strengthens article credibility).
- Per-shot xG gap: accept shot-count outcomes (recommended, spec-compliant) or discuss alternative xG sources.
- `WC2026_104_games_narration.pdf` still missing (video-writing stage only).
- Milestone gating: user approves each phase; M2 analysis phase (§7.1–7.5) is approved and next.
