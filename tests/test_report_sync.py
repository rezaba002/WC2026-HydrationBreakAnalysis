"""Prose must agree with the computed numbers. Enforced, not remembered.

Every review round of this project found the same defect class: the analysis was
corrected, the tables regenerated, and the hand-written prose kept quoting the
old numbers. Stale clock probabilities, an obsolete robustness summary, and
three separate "every interval includes zero" sentences that had become false
while sitting next to a table that contradicted them.

These tests make that failure mode mechanical:

  1. Every headline number quoted in README.md and REPORT.md must equal the
     value in reports/facts.json (regenerated from the tables by src.facts).
  2. No generated table may assert that ALL of something's intervals include
     zero unless that is actually true of every interval in the file. Modules
     needing a scoped statement must generate it with facts.interval_sentence(),
     which counts rather than universalises.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from src import facts

ROOT = Path(__file__).resolve().parents[1]
FACTS_JSON = ROOT / "reports" / "facts.json"

_NUM = r"[-−+]?\d+(?:\.\d+)?"
_INTERVAL = re.compile(rf"\[\s*({_NUM})\s*,\s*({_NUM})\s*\]")

# Sentences claiming universal inclusion of zero. Banned unless globally true.
_UNIVERSAL = re.compile(
    r"(?:\*\*)?(?:every|all)\b[^.\n]{0,60}?intervals?\b[^.\n]{0,30}?includes?\s+zero",
    re.IGNORECASE,
)


@pytest.fixture(scope="module")
def facts_data():
    """Rebuild facts from the committed tables so the test never reads a stale file."""
    return facts.collect()


def test_facts_json_is_current(facts_data):
    """reports/facts.json must be regenerated whenever the tables change."""
    assert FACTS_JSON.exists(), "run `python -m src.facts`"
    on_disk = json.loads(FACTS_JSON.read_text(encoding="utf-8"))
    for section in facts_data:
        if section == "generated":
            continue
        assert on_disk.get(section) == facts_data[section], (
            f"reports/facts.json is stale in section {section!r} — "
            "run `python -m src.facts` and commit the result"
        )


def test_the_primary_sample_is_183_and_common_support_is_a_subset(facts_data):
    """One primary sample, declared once. 148 is a subset of 183, not a rival."""
    assert facts_data["test_a"]["primary"]["breaks"] == 183
    assert facts_data["e1"]["common_support_breaks"] == 148
    assert facts_data["e1"]["common_support_breaks"] < facts_data["test_a"]["primary"]["breaks"]


def _flat(doc: str) -> str:
    """Normalise a document for matching.

    Collapses whitespace so a re-wrapped paragraph does not defeat a check, and
    strips bold/italic markers so `**0.689**` and `0.689` are the same number.
    """
    text = (ROOT / doc).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", text.replace("*", ""))


@pytest.mark.parametrize("doc", facts.DOCS)
def test_prose_numbers_match_the_computed_facts(doc, facts_data):
    """Any headline number in the prose must equal the generated value."""
    text = _flat(doc)
    matched = set()
    for path, pattern in facts.DOC_CHECKS:
        for m in re.finditer(pattern, text):
            expected = facts.lookup(facts_data, path)
            # Patterns may alternate over several documents' phrasings; take
            # whichever branch actually captured.
            captured = next((g for g in m.groups() if g is not None), None)
            assert captured is not None, f"{path} pattern matched but captured nothing"
            got = float(captured.replace("−", "-"))
            assert abs(got - float(expected)) < 1e-9, (
                f"{doc} quotes {got} for {path}, but the tables now say {expected}. "
                f"Context: {m.group(0)!r}. Fix the prose — do not edit facts.json."
            )
            matched.add(path)
    floor = facts.MIN_CHECKS[doc]
    assert len(matched) >= floor, (
        f"{doc} only exercised {len(matched)} of {len(facts.DOC_CHECKS)} checks "
        f"(floor {floor}). Missing: "
        f"{sorted({k for k, _ in facts.DOC_CHECKS} - matched)}. A check that never "
        "matches cannot fail — realign the pattern or the prose."
    )


def test_readme_covers_the_headline_facts(facts_data):
    """The specific numbers that went stale before must be present and correct."""
    text = _flat("README.md")
    for path in ("clock.display_w8.observed", "clock.adjusted_w8.observed",
                 "test_a.primary.effect", "perception.unique_supported"):
        # A fact may have several registered phrasings; any one of them counts.
        patterns = [p for k, p in facts.DOC_CHECKS if k == path]
        assert any(re.search(p, text) for p in patterns), (
            f"README no longer states {path}; either restore it or drop the check"
        )


@pytest.mark.parametrize("table", sorted((ROOT / "reports" / "tables").glob("*.md")))
def test_no_generated_table_universalises_a_false_interval_claim(table):
    """'Every interval includes zero' must be true of every interval in the file.

    This is the exact sentence that went false three times while sitting beside
    a table disproving it.
    """
    text = table.read_text(encoding="utf-8")
    claims = _UNIVERSAL.findall(text)
    if not claims:
        return
    intervals = [(float(a.replace("−", "-")), float(b.replace("−", "-")))
                 for a, b in _INTERVAL.findall(text)]
    offenders = [iv for iv in intervals if facts.excludes_zero(*iv)]
    assert not offenders, (
        f"{table.name} claims all intervals include zero, but "
        f"{len(offenders)} of {len(intervals)} exclude it: {offenders}. "
        "Use facts.interval_sentence() to generate a counted statement instead."
    )


@pytest.mark.parametrize("doc", facts.DOCS)
def test_prose_does_not_universalise_a_false_interval_claim(doc):
    text = (ROOT / doc).read_text(encoding="utf-8")
    if not _UNIVERSAL.search(text):
        return
    intervals = [(float(a.replace("−", "-")), float(b.replace("−", "-")))
                 for a, b in _INTERVAL.findall(text)]
    offenders = [iv for iv in intervals if facts.excludes_zero(*iv)]
    assert not offenders, f"{doc} universalises an interval claim contradicted by {offenders}"


def test_report_test_b_table_matches_the_computed_values(facts_data):
    """The report transcribes Test B into its own table; verify every cell.

    A hand-transcribed table is the same defect surface as hand-typed prose, and
    regex-per-cell is too brittle — so parse the table and compare it wholesale.
    """
    text = (ROOT / "reports" / "final" / "REPORT.md").read_text(encoding="utf-8")
    rows = {}
    for line in text.splitlines():
        m = re.match(rf"\|\s*(\d+) min\s*\|\s*(\d+)\s*\|\s*({_NUM})\s*\|\s*({_NUM})\s*\|"
                     rf"\s*\**({_NUM})\**\s*\|\s*\[({_NUM}),\s*({_NUM})\]", line.strip())
        if m:
            rows[int(m.group(1))] = [float(g.replace("−", "-")) for g in m.groups()[1:]]
    assert set(rows) == {5, 8, 10}, f"Test B table not found in the report (got {sorted(rows)})"
    for w, (breaks, real, ctrl, d, lo, hi) in rows.items():
        f = facts_data["test_b"][f"w{w}"]
        assert breaks == f["breaks"], f"w={w} breaks: report {breaks}, computed {f['breaks']}"
        for label, got, want in (("swing_real", real, f["swing_real"]),
                                 ("swing_control", ctrl, f["swing_control"]),
                                 ("D", d, f["D"]),
                                 ("ci_lo", lo, f["ci"][0]), ("ci_hi", hi, f["ci"][1])):
            assert abs(got - want) < 5e-4, (
                f"w={w} {label}: report {got}, computed {want} — regenerate the report table")


@pytest.mark.parametrize("doc", facts.DOCS)
def test_every_referenced_figure_exists(doc):
    """A document may not reference a figure that was never generated.

    An external draft of the article cited four plausible-looking figure names
    that did not exist. Broken images survive proofreading easily; they do not
    survive this.
    """
    path = ROOT / doc
    text = path.read_text(encoding="utf-8")
    missing = []
    for rel in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        if rel.startswith(("http://", "https://")):
            continue
        if not (path.parent / rel).resolve().exists():
            missing.append(rel)
    assert not missing, f"{doc} references figures that do not exist: {missing}"


def test_article_quotes_carry_a_verified_source():
    """Every quotation in the article must trace to the verified claim files.

    Three collected quotes failed source verification and are excluded from the
    project; an external draft reintroduced one in altered wording under the
    wrong outlet. Quotes are checked verbatim against what was actually logged.
    """
    import csv

    raw = (ROOT / "reports" / "final" / "ARTICLE.md").read_text(encoding="utf-8")
    # Strip blockquote markers first: a quotation wrapped across two lines
    # carries a "> " into the middle of its own text.
    article = re.sub(r"^>\s?", "", raw, flags=re.MULTILINE)
    quoted = re.findall(r'"([^"]+)"', article)
    quoted = [q for q in quoted if len(q.split()) >= 5]   # ignore short scare-quotes
    assert quoted, "no quotations found — did the article's quote format change?"

    logged = []
    for name in ("perception_claims.csv", "perception_rejections.csv"):
        with open(ROOT / "data" / "manual" / name, encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                for key in ("claim_text", "candidate_text"):
                    if row.get(key):
                        logged.append(re.sub(r"\s+", " ", row[key]).strip().lower())

    # Case-insensitive: a quote embedded mid-sentence legitimately lowercases
    # its first letter. Wording, not capitalisation, is what must match.
    for q in quoted:
        needle = re.sub(r"\s+", " ", q).strip().rstrip(".,").lower()
        assert any(needle in entry for entry in logged), (
            f"Article quotes text with no verified source record: {needle!r}. "
            "Every quotation must appear verbatim in data/manual/perception_*.csv."
        )


def test_interval_sentence_counts_rather_than_universalises():
    """The generator itself must not produce a false universal."""
    assert "Every" in facts.interval_sentence([(-1.0, 1.0), (-0.5, 0.5)], "x")
    mixed = facts.interval_sentence([(-1.0, 1.0), (0.001, 0.5)], "x")
    assert "1 of 2" in mixed and "exclude zero" in mixed
    assert not _UNIVERSAL.search(mixed)
    allbad = facts.interval_sentence([(0.1, 1.0), (0.2, 0.5)], "x")
    assert "excludes zero" in allbad


def test_no_document_claims_robustness_across_all_specifications():
    """The support sensitivity drifts; 'robust across all specifications' is false."""
    banned = re.compile(
        r"robust (?:across|to) all (?:specifications|checks|cuts)|"
        r"stable across all|definitively no (?:competitive )?effect|"
        r"(?:holds|survives) (?:under )?every specification|"
        r"proves? (?:there was )?no effect|no effect whatsoever",
        re.IGNORECASE)
    for doc in facts.DOCS + ["reports/tables/robustness.md"]:
        text = (ROOT / doc).read_text(encoding="utf-8")
        hit = banned.search(text)
        assert not hit, f"{doc} overclaims: {hit.group(0)!r} (see facts.json test_a.min10)"
