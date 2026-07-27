# Did hydration breaks change the 2026 World Cup?

An independent analysis of **203 recorded mandatory hydration breaks across 102 matches**
of the 2026 FIFA World Cup, prospectively specified in a frozen, timestamped Git
specification (not lodged in an external registry) — the first tournament to stop every match twice
regardless of weather. (Coverage is 203 of a possible 204 breaks in 102 of 104 matches;
every exclusion is documented.)

📄 **[Read the report (PDF)](reports/final/WC2026_Hydration_Break_Report.pdf)** ·
[Markdown version](reports/final/REPORT.md) ·
[Frozen specification](spec.md) · [Amendments & limitations](CHANGELOG.md)

---

## Three findings

**1. The average competitive effect is null — and the obvious counter-evidence is a clock
artifact.** Measured on the display clock, where the 8-minute post-break window *starts at
the break and includes the stoppage*, the probability of a shot collapses to 0.689. Remove
the three dead minutes and it is 0.818 against a null of 0.787: ordinary. The apparent
post-break shot drought was largely stopped time counted as football. On the primary metric
— the primary Test A sample of **183 breaks** across 101 matches — the paired effect is
**−0.073 shots, 95% match-clustered
CI [−0.258, +0.116]** — no detectable difference from comparable ordinary minutes.

*With one caveat we state up front:* demanding deeper control support moves that estimate
steadily more negative (−0.073 → −0.173 → −0.196 → −0.948), and the strictest cut excludes
zero. That cut rests on 18 breaks in quiet, heavily selected matches, so it is consistent
with selection rather than a stronger effect — but the null is **not** robust to it, and
anyone citing the headline should cite this alongside it.

And the directional version, which is what people actually claim: among breaks with an
identifiable and matchable attacking side (88 / 63 / 33 at the 5 / 8 / 10-minute windows),
that team gave back **~1 shot of advantage** afterwards — but no more than after comparable
uninterrupted spells (D = −0.136 / −0.251 / +0.258, every interval spanning zero). The
collapse fans remember is real; we find no detectable additional loss associated with the
break.

**2. Substitutions moved rather than multiplied.** Only 18.7% of second-half substitutions
fell within ±3 minutes of their own match's break — *below* the minute-matched historical
rate. But there is a deficit in the 3 minutes before the stoppage and a surplus in the 3
minutes after the restart. Coaches waited for the break, then acted.

**3. Public claims were right about half the time — but attached to almost nothing.** A
stratified random sweep found claims on just **4 of 48 sampled breaks (8.3%, 95% CI
3.3–19.6%)**. Among verified claims, **7 of 12 unique claimed breaks** were supported
(8 of 16 at claim level). Observers were not inventing swings; they were describing a tiny,
memorable, unrepresentative slice of them.

![Real breaks vs 10,000 comparable moments](reports/figures/fig_placebo.png)

---

## Outputs

| # | Core output | Status | Result |
|---|---|---|---|
| 1 | Source audit & master tables | ✅ | [source_inventory.csv](data/processed/source_inventory.csv), [audit_claims.md](reports/tables/audit_claims.md) |
| 2 | Independent shot-event layer (no per-shot xG exists — see limitations) | ✅ | 2,554 shots, 1,914 subs, 3,073 physical rows from FIFA PMSRs |
| 3 | Dual-clock matched counterfactual (Test A) | ✅ | [placebo_results.md](reports/tables/placebo_results.md) · [robustness.md](reports/tables/robustness.md) |
| 3b | State-matched directional test (Test B) | ✅ | [test_b.md](reports/tables/test_b.md) |
| 4 | Substitution timing vs 2018/2022 | ✅ | [subs_timing.md](reports/tables/subs_timing.md) |
| 5 | Preregistered perception dataset | ✅ | [perception.md](reports/tables/perception.md) · [codebook](docs/perception_codebook.md) |
| 6 | Added time & duration | ✅ | [added_time.md](reports/tables/added_time.md) |
| 7 | Case studies (2×2 selection) | ✅ | [case_studies.md](reports/tables/case_studies.md) |
| + | Fresh-legs deployment · late-game proxy | ✅ | [physical_freshlegs.md](reports/tables/physical_freshlegs.md) · [late_game.md](reports/tables/late_game.md) |
| E1 | Clock-artefact decomposition (exploratory) | ✅ | [break_window.md](reports/tables/break_window.md) |
| A | Appendix — yellow-card rates (weak proxy) | ✅ | [cards.md](reports/tables/cards.md) |
| C | Commercial inventory arithmetic | ✅ | [commercial.md](reports/tables/commercial.md) |

Twelve figures in [reports/figures/](reports/figures/).

**Every number quoted in this README and in the report is generated into
[reports/FACTS.md](reports/FACTS.md) by `python -m src.facts`, and
`tests/test_report_sync.py` fails the build if any document drifts from it.**

## Why you might trust it

- The analysis specification was **frozen before any outcome was computed** ([spec.md](spec.md)); every later change is dated in [CHANGELOG.md](CHANGELOG.md).
- A strong, robustness-passing directional result was **found and then deleted** once its control pool proved biased (CHANGELOG A5).
- The perception sample was drawn **at random and pre-specified**, not chosen from famous matches — and null results are logged.
- Every quote was **re-read against its source**; three failed and are excluded from all figures.
- A control-window contamination defect was found and fixed after publication (CHANGELOG A7); the samples and estimates it changed are reported, not quietly replaced.
- The test suite validates IDs, break uniqueness, clock arithmetic, control-pool integrity, table consistency — and that **the prose still matches the computed numbers**, so a corrected figure cannot leave a stale sentence behind.

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
python -m src.cards             # appendix: yellow-card rates
python -m src.commercial        # commercial inventory arithmetic
python -m src.physical          # fresh-legs deployment
python -m src.late_game         # late-game proxy
python -m src.charts            # figures
python -m src.facts             # regenerate reports/facts.json + FACTS.md
python -m src.make_pdf          # report PDF
python -m pytest tests -q       # incl. prose-vs-numbers sync checks
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
