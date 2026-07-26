# Did hydration breaks change the 2026 World Cup?

An independent, preregistered analysis of **203 recorded mandatory hydration breaks across
102 matches** of the 2026 FIFA World Cup — the first tournament to stop every match twice
regardless of weather. (Coverage is 203 of a possible 204 breaks in 102 of 104 matches;
every exclusion is documented.)

📄 **[Read the report (PDF)](reports/final/WC2026_Hydration_Break_Report.pdf)** ·
[Markdown version](reports/final/REPORT.md) ·
[Frozen specification](spec.md) · [Amendments & limitations](CHANGELOG.md)

---

## Three findings

**1. The average competitive effect is null — and the obvious counter-evidence is a clock
artifact.** Measured on the display clock, where the 8-minute post-break window *starts at
the break and includes the stoppage*, the probability of a shot collapses to 0.658 against
a ~0.80 baseline. Remove the three dead minutes and it is 0.806 against a null of 0.822:
ordinary. The apparent post-break shot drought was largely stopped time counted as
football. On the primary metric the paired effect is **−0.085 shots, 95% match-clustered
CI [−0.238, +0.074]** — no detectable difference from comparable ordinary minutes.

And the directional version, which is what people actually claim: a team that had been
dominating gives back **~1 shot of advantage** after a break — and gives back the same
after uninterrupted spells of identical dominance (difference −0.01 to −0.10, all
intervals spanning zero). The collapse fans remember is real; it is what dominance
normally does.

**2. Substitutions moved rather than multiplied.** Only 18.7% of second-half substitutions
fell within ±3 minutes of their own match's break — *below* the minute-matched historical
rate. But there is a deficit in the 3 minutes before the stoppage and a surplus in the 3
minutes after the restart. Coaches waited for the break, then acted.

**3. Public claims were right about half the time — but attached to almost nothing.** A
stratified random sweep found claims on just **4 of 48 sampled breaks (8.3%, 95% CI
3.3–19.6%)**. Among verified claims, **7 of 13 unique claimed breaks** were supported
(8 of 17 at claim level). Observers were not inventing swings; they were describing a tiny,
memorable, unrepresentative slice of them.

![Real breaks vs 10,000 comparable moments](reports/figures/fig_placebo.png)

---

## Outputs

| # | Core output | Status | Result |
|---|---|---|---|
| 1 | Source audit & master tables | ✅ | [source_inventory.csv](data/processed/source_inventory.csv), [audit_claims.md](reports/tables/audit_claims.md) |
| 2 | Independent shot/xG layer | ✅ | 2,554 shots, 1,914 subs, 3,073 physical rows from FIFA PMSRs |
| 3 | Dual-clock randomized placebo (Test A) | ✅ | [placebo_results.md](reports/tables/placebo_results.md) · [robustness.md](reports/tables/robustness.md) |
| 3b | State-matched directional test (Test B) | ✅ | [test_b.md](reports/tables/test_b.md) |
| 4 | Substitution timing vs 2018/2022 | ✅ | [subs_timing.md](reports/tables/subs_timing.md) |
| 5 | Preregistered perception dataset | ✅ | [perception.md](reports/tables/perception.md) · [codebook](docs/perception_codebook.md) |
| 6 | Added time & duration | ✅ | [added_time.md](reports/tables/added_time.md) |
| 7 | Case studies (2×2 selection) | ✅ | [case_studies.md](reports/tables/case_studies.md) |
| + | Fresh-legs deployment · late-game proxy | ✅ | [physical_freshlegs.md](reports/tables/physical_freshlegs.md) · [late_game.md](reports/tables/late_game.md) |

Twelve figures in [reports/figures/](reports/figures/).

## Why you might trust it

- The analysis specification was **frozen before any outcome was computed** ([spec.md](spec.md)); every later change is dated in [CHANGELOG.md](CHANGELOG.md).
- A strong, robustness-passing directional result was **found and then deleted** once its control pool proved biased (CHANGELOG A5).
- The perception sample was drawn **at random and pre-specified**, not chosen from famous matches — and null results are logged.
- Every quote was **re-read against its source**; three failed and are excluded from all figures.
- 38 tests validate IDs, break uniqueness, clock arithmetic, control-pool integrity and table consistency.

## Reproduce

```bash
pip install -r requirements.txt

# Fetch the inputs this repo reads but does not redistribute (see LICENSE).
# --metadata-only is enough to run the full test suite; omit it to regenerate
# the analysis end to end.
bash scripts/fetch_external.sh

python -m src.audit             # source inventory + hashes
python -m src.build_tables      # matches / breaks / venues / exclusions / coverage
python -m src.clocks            # break-adjusted clock bands
python -m src.statsbomb_extract # WC2018 + WC2022 baselines
python -m src.fetch_fifa_pdfs   # FIFA PMSRs (cached; --discover-only to skip)
python -m src.parse_fifa_pdfs   # shots / subs / physical / team stats
python -m src.placebo           # Core Output 3
python -m src.robustness        # robustness pass
python -m src.subs              # Core Output 4
python -m src.perception        # Core Output 5
python -m src.added_time        # Core Output 6
python -m src.case_studies      # Core Output 7
python -m src.test_b            # Test B: state-matched directional (spec 5)
python -m src.break_window      # clock-artefact analysis (exploratory, E1)
python -m src.break_window      # clock-artefact analysis (exploratory, E1)
python -m src.physical          # fresh-legs deployment
python -m src.late_game         # late-game proxy
python -m src.charts            # figures
python -m src.make_pdf          # report PDF
python -m pytest tests -q
```

Python 3.11. `make_pdf` renders via headless Edge/Chromium.

## Data availability

Project-generated tables (`data/processed/`, `data/manual/`) and figures are committed and
MIT-licensed. **Third-party source data is not redistributed**: FIFA PMSR PDFs are fetched
into a gitignored `data/raw/`, and SofaScore-derived momentum values are used only as a
labelled secondary outcome. Provenance, commit hashes and SHA-256 checksums for every input
are in [config/sources.yaml](config/sources.yaml) and
[source_inventory.csv](data/processed/source_inventory.csv). See [LICENSE](LICENSE) for the
full scope note.

## Limitations

Per-shot xG does not exist in any independently auditable source, so outcomes are
shot-based. **Home/away-oriented** results are not reportable — the control pool is biased
for that particular signed contrast (CHANGELOG A5); the directional Test B avoids it by
orienting on pre-window dominance instead, symmetrically in both arms, with the control
composition standardised. Test B is descriptive by design, not causal. Exact 2026 added
time is unavailable, so only a lower bound is given. No physiological claim is made anywhere: public event data cannot support one.
Perception collection covers 24 of 104 matches by random sweep plus a topical pass. Full
list in [report §8](reports/final/REPORT.md).

## Citation

See [CITATION.cff](CITATION.cff), or:

> Baghestani, R. (2026). *Did hydration breaks change the 2026 World Cup? A reproducible
> analysis of 203 mandatory breaks.* https://github.com/rezaba002/WC2026-HydrationBreakAnalysis
