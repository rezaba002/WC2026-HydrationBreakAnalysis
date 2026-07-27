# Publication

Audience-facing versions of this project. Everything here is *derived* — it adds no
analysis, and no number in it is typed by hand.

| file | what it is |
|---|---|
| [ARTICLE.md](ARTICLE.md) | General-audience article, ~2,950 words, 14 figures |
| [WC2026_Hydration_Breaks_Article.pdf](WC2026_Hydration_Breaks_Article.pdf) | Print/share version of the same, figures embedded |

The technical deliverable lives elsewhere and is a different document for a different
reader: [`reports/final/REPORT.md`](../reports/final/REPORT.md) and its PDF.

## The rules everything here follows

Every number is generated into [`reports/facts.json`](../reports/facts.json) by
`python -m src.facts`, and `tests/test_report_sync.py` fails the build if any document
disagrees with it. Three checks apply specifically to this folder:

- **Numbers** — 27 anchored checks tie the article's figures to the computed tables, with a
  coverage floor so a pattern that stops matching cannot pass silently.
- **Figures** — every referenced image must exist. An external draft of this article cited
  four plausible-looking filenames that had never been generated.
- **Quotes** — every quotation must appear verbatim in
  [`data/manual/`](../data/manual/) `perception_claims.csv` or `perception_rejections.csv`.
  Quotes in this project were re-read against their source URLs; three failed and are
  excluded everywhere. The same external draft altered a Tuchel quote and attributed it to
  the wrong outlet, which is why this is enforced rather than trusted.

## Rebuilding

```bash
python -m src.facts             # regenerate the numbers
python -m src.article_figures   # regenerate art_*.png from facts.json
python -m src.make_pdf article  # rebuild this PDF (omit "article" for both)
python -m pytest tests -q
```

Figures are shared with the report and live in [`reports/figures/`](../reports/figures/).
The six `art_*.png` charts are built for the article specifically; the rest are reused.

`ARTICLE.html` is a build intermediate with figures base64-inlined and is not committed.
