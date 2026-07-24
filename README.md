# WC2026 Hydration Break Impact

Reproducible analysis of the 2026 World Cup's universal hydration-break policy:
perceived impact vs measurable competitive impact vs structural impact.
Final outputs: comprehensive report, charts, and a 6–7 minute SportOnTheLine video.

**The analysis design is frozen** — see [spec.md](spec.md) and
[config/analysis_spec.yaml](config/analysis_spec.yaml). The single biggest project
risk is scope creep: no new analytical branches until the seven core outputs exist.

## Seven core outputs

1. Source audit and master tables ✅ (Milestone 1)
2. Independent shot/xG data layer
3. Dual-clock randomized placebo analysis ← *the chart the video is built on*
4. Substitution timing vs 2018 and 2022
5. Preregistered perception dataset (templates ✅)
6. Added-time comparison across three World Cups
7. Three tactical + three null case studies

## Reproducing Milestone 1

```powershell
pip install -r requirements.txt
# external repos must be cloned into external/ (see config/sources.yaml)
python -m src.audit             # source inventory + README-claims check
python -m src.build_tables      # matches/venues/breaks/exclusions/coverage
python -m src.provisional_null  # audit null + reference verification
python -m src.charts            # break-timing + WBGT figures
python -m pytest tests -q
```

## Layout

```
config/           frozen spec (YAML) + source provenance
external/         cloned source repos (never edited, never committed)
data/processed/   master tables built by src/
data/manual/      perception-claim templates (preregistered; codebook in docs/)
src/              pipeline modules (audit, build_tables, provisional_null, charts)
reports/          figures + tables
tests/            validation suite for the master tables
MILESTONE_1_REPORT.md
```

## Rules

- Raw/external data is never edited in place; every transformation is code.
- No result exists only inside a notebook.
- Exclusions are never hidden — see `data/processed/exclusions.csv`.
- Effect sizes and compatibility intervals, not p-values; n reported in breaks and
  matches, never team-rows.
