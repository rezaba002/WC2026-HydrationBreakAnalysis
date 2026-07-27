"""Single source of numeric truth for every prose document in this repository.

WHY THIS EXISTS
---------------
Through five review rounds the analysis kept getting more correct while the
README and the report kept going stale, because headline numbers were re-typed
by hand into prose after every rerun. That is the largest recurring defect class
in this project's history (stale clock probabilities, an obsolete robustness
summary, contradictory interval sentences, wrong sample sizes).

This module ends that by making the generated tables the ONLY place a number is
computed, and this file the only place a number is quoted from. Prose documents
(README.md, reports/final/REPORT.md, the article, the video script) must agree
with `reports/facts.json`; `tests/test_report_sync.py` fails the build if they
drift.

Nothing here computes statistics. It reads what the analysis modules already
wrote and republishes it in one machine-readable place.

Outputs:
  reports/facts.json   machine-readable, consumed by tests
  reports/FACTS.md     human-readable fact sheet — write the article from THIS

Run:  python -m src.facts
"""
from __future__ import annotations

import json
import re
from datetime import date

from .util import REPORTS, TABLES, excludes_zero, interval_sentence  # noqa: F401

# --------------------------------------------------------------------------
# THE PRIMARY SAMPLE — declared once, here, and labelled everywhere.
#
# Two different break counts are legitimate and are constantly confused:
#   183  the primary Test A sample: 8-minute window, every break with at least
#        one clean control minute at that window.
#   148  the cross-window common-support sample: breaks simultaneously valid at
#        w = 3, 5, 8 and 10, required by E1 so the four windows describe the
#        same matches. It is a SUBSET of 183, not a correction to it.
# --------------------------------------------------------------------------
PRIMARY_SAMPLE_NOTE = (
    "Primary Test A sample = 183 breaks (8-minute window, maximal clean control "
    "support). The cross-window common-support sample = 148 breaks (valid at all "
    "of w=3/5/8/10 simultaneously), used only by the exploratory E1 decomposition."
)

_NUM = r"[-−+]?\d+(?:\.\d+)?"


def _f(s: str) -> float:
    """Parse a number that may use a Unicode minus."""
    return float(str(s).replace("−", "-").replace("+", "").strip())


def _read(name: str) -> str:
    return (TABLES / name).read_text(encoding="utf-8")


def _row(text: str, key: str) -> list[str]:
    """Return the cells of the first table row containing `key`."""
    for line in text.splitlines():
        if line.lstrip().startswith("|") and key in line:
            return [c.strip() for c in line.strip().strip("|").split("|")]
    raise KeyError(f"no table row containing {key!r}")


def _ci(cell: str) -> tuple[float, float]:
    m = re.search(rf"\[\s*({_NUM})\s*,\s*({_NUM})\s*\]", cell)
    if not m:
        raise ValueError(f"no interval in {cell!r}")
    return _f(m.group(1)), _f(m.group(2))


def _grab(text: str, pattern: str, group: int = 1) -> str:
    m = re.search(pattern, text)
    if not m:
        raise ValueError(f"pattern not found: {pattern}")
    return m.group(group)


# `excludes_zero` and `interval_sentence` live in util so the analysis modules
# can generate their own interval prose without importing this reporting layer.

# --------------------------------------------------------------------------
# Extractors — one per generated table.
# --------------------------------------------------------------------------
def test_a() -> dict:
    t = _read("robustness.md")
    out = {}
    for key, label in [("preregistered Test A", "primary"),
                       ("min 3 controls", "min3"),
                       ("min 5 controls", "min5"),
                       ("min 10 controls", "min10")]:
        # | variant | breaks | matches | median controls | paired effect | 95% CI |
        c = _row(t, key)
        lo, hi = _ci(c[5])
        out[label] = {"breaks": int(c[1]), "matches": int(c[2]),
                      "median_controls": int(c[3]),
                      "effect": _f(c[4]), "ci": [lo, hi],
                      "excludes_zero": excludes_zero(lo, hi)}
    loo = re.search(rf"Leave-one-match-out range:\s*\*\*\[({_NUM}),\s*({_NUM})\]\*\*"
                    rf"\s*across\s*(\d+)", t)
    out["loo"] = {"lo": _f(loo.group(1)), "hi": _f(loo.group(2)),
                  "refits": int(loo.group(3))}
    return out


def clock() -> dict:
    t = _read("placebo_results.md")
    out = {}
    for ck in ("display", "adjusted"):
        for w in (5, 8, 10):
            c = _row(t, f"| {ck} | {w} | next_shot_within_w")
            out[f"{ck}_w{w}"] = {"observed": _f(c[3]), "null": _f(c[4])}
    out["analysed_breaks"] = int(_grab(t, r"Breaks analysed:\s*(\d+)"))
    out["total_breaks"] = int(_grab(t, r"Breaks analysed:\s*\d+ of (\d+)"))
    return out


def test_b() -> dict:
    t = _read("test_b.md")
    out = {}
    for w in (5, 8, 10):
        c = _row(t, rf"| {w} | ")
        lo, hi = _ci(c[7])
        out[f"w{w}"] = {"breaks": int(c[1]), "matches": int(c[2]),
                        "pre_advantage": _f(c[3]), "swing_real": _f(c[4]),
                        "swing_control": _f(c[5]),
                        "D": _f(c[6].replace("**", "")), "ci": [lo, hi],
                        "excludes_zero": excludes_zero(lo, hi)}
    return out


def e1() -> dict:
    t = _read("break_window.md")
    n, m = re.search(r"breaks valid at all windows \((\d+) breaks / (\d+) matches", t).groups()
    out = {"common_support_breaks": int(n), "common_support_matches": int(m),
           "D": {}, "A": {}}
    d_block = t.split("### Transition-minute sensitivity")[0]
    a_block = t.split("## Validation 1")[1].split("### Sensitivity")[0]
    for w in (3, 5, 8, 10):
        c = _row(d_block, rf"| {w} | ")
        lo, hi = _ci(c[7])
        out["D"][f"w{w}"] = {"value": _f(c[6].replace("**", "")), "ci": [lo, hi],
                             "excludes_zero": excludes_zero(lo, hi)}
        c = _row(a_block, rf"| {w} | ")
        lo, hi = _ci(c[4])
        out["A"][f"w{w}"] = {"value": _f(c[3].replace("**", "")), "ci": [lo, hi],
                             "excludes_zero": excludes_zero(lo, hi)}
    return out


def perception() -> dict:
    t = _read("perception.md")
    u = re.search(r"unique claimed breaks \(verified\): (\d+)/(\d+) \((\d+)%\)", t)
    c = re.search(r"Claim-level, for comparison: (\d+)/(\d+) \((\d+)%\)", t)
    s = re.search(r"\*\*(\d+) of (\d+) sampled breaks \(([\d.]+)%, 95% CI ([\d.]+)-([\d.]+)%\)\*\*", t)
    return {
        "unique_supported": int(u.group(1)), "unique_total": int(u.group(2)),
        "unique_pct": int(u.group(3)),
        "claim_supported": int(c.group(1)), "claim_total": int(c.group(2)),
        "claim_pct": int(c.group(3)),
        "sweep_with_claims": int(s.group(1)), "sweep_n": int(s.group(2)),
        "sweep_pct": float(s.group(3)),
        "sweep_ci": [float(s.group(4)), float(s.group(5))],
        "claims_collected": int(_grab(t, r"Claims collected: (\d+)")),
        "claims_verified": int(_grab(t, r"source-verified: (\d+)")),
        "breaks_with_claims": int(_grab(t, r"claims on (\d+) of \d+ breaks")),
    }


def subs() -> dict:
    t = _read("subs_timing.md")
    m = re.search(r"break: \*\*(\d+)/(\d+) = ([\d.]+)%\*\*", t)
    return {
        "at_break": int(m.group(1)), "h2_total": int(m.group(2)),
        "pct": float(m.group(3)),
        "exp_2018": float(_grab(t, r"expectation from WC2018: ([\d.]+)%")),
        "exp_2022": float(_grab(t, r"expectation from WC2022: ([\d.]+)%")),
        "before_2026": float(_grab(t, r"before the stoppage: 2026 ([\d.]+)%")),
        "after_2026": float(_grab(t, r"from the restart: 2026 ([\d.]+)%")),
    }


def cards() -> dict:
    t = _read("cards.md")
    out = {}
    for w in (5, 8, 10):
        c = _row(t, rf"| {w} | ")
        lo, hi = _ci(c[8])
        out[f"w{w}"] = {"breaks": int(c[1]), "D": _f(c[7].replace("**", "")),
                        "ci": [lo, hi], "excludes_zero": excludes_zero(lo, hi)}
    # The goal-depletion artefact: why goals cannot be an outcome here.
    out["goals_real_w8"] = _f(_grab(t, r"\| real break windows \| ([\d.]+) \|"))
    out["goals_control_w8"] = _f(_grab(t, r"\| matched control windows \| ([\d.]+) \|"))
    out["n_goals"] = int(_grab(t, r"than cards \((\d+) vs \d+\)"))
    out["n_cards"] = int(_grab(t, r"than cards \(\d+ vs (\d+)\)"))
    return out


def commercial() -> dict:
    t = _read("commercial.md")
    return {
        "break_minutes": int(_grab(t, r"\| (\d+) min \(([\d.]+) hours\)")),
        "break_hours": float(_grab(t, r"\| \d+ min \(([\d.]+) hours\)")),
        "per_match_min": float(_grab(t, r"\| Per match \| ([\d.]+) min")),
        "policy_slots": int(_grab(t, r"\| (\d+) slots across")),
        "policy_hours": float(_grab(t, r"~([\d.]+) hours")),
    }


def added_time() -> dict:
    t = _read("added_time.md")
    return {
        "h2_end_2018": float(_grab(t, r"\| WC2018 \| exact half-end \| \d+ \| \+[\d.]+' \| \+[\d.]+' \| ([\d.]+)'")),
        "h2_end_2022": float(_grab(t, r"\| WC2022 \| exact half-end \| \d+ \| \+[\d.]+' \| \+[\d.]+' \| ([\d.]+)'")),
        "h2_floor_2026": float(_grab(t, r"\| WC2026 \|.*?\| ([\d.]+)'")),
        "late_goals_2018": float(_grab(t, r"\| WC2018 \| ([\d.]+)% \|")),
        "late_goals_2022": float(_grab(t, r"\| WC2022 \| ([\d.]+)% \|")),
        "late_goals_2026": float(_grab(t, r"\| WC2026 \| ([\d.]+)% \|")),
    }


def collect() -> dict:
    return {
        "generated": date.today().isoformat(),
        "primary_sample_note": PRIMARY_SAMPLE_NOTE,
        "test_a": test_a(),
        "clock": clock(),
        "test_b": test_b(),
        "e1": e1(),
        "perception": perception(),
        "subs": subs(),
        "cards": cards(),
        "commercial": commercial(),
        "added_time": added_time(),
    }


# --------------------------------------------------------------------------
# Prose checks: (dotted fact path, regex with ONE capture group, files)
#
# The sync test finds each regex in each document and asserts the captured
# number equals the fact. This is what catches "0.658 where 0.689 belongs".
# --------------------------------------------------------------------------
DOCS = ["README.md", "reports/final/REPORT.md"]

#
# Patterns are matched against a normalised document: whitespace collapsed and
# bold/italic markers stripped, so re-wrapping a paragraph or bolding a number
# cannot silently disable a check.
DOC_CHECKS: list[tuple[str, str]] = [
    # The clock artefact — the numbers that went stale twice.
    ("clock.display_w8.observed",
     rf"probability of a shot (?:in that window )?(?:collapses|falls) to ({_NUM})"),
    ("clock.adjusted_w8.observed",
     rf"(?:break-adjusted clock (?:the same )?probability is|"
     rf"Remove the three dead minutes and it is) ({_NUM})"),
    ("clock.adjusted_w8.null",
     rf"(?:break-adjusted clock (?:the same )?probability is|"
     rf"Remove the three dead minutes and it is) {_NUM} against a null of ({_NUM})"),
    # Test A headline.
    ("test_a.primary.effect", rf"(?:paired effect is|Effect:) ({_NUM}) shots"),
    ("test_a.primary.ci.0", rf"95% match-clustered CI \[({_NUM}),"),
    ("test_a.primary.ci.1", rf"95% match-clustered CI \[{_NUM}, ({_NUM})\]"),
    ("test_a.primary.breaks",
     r"(?:primary Test A sample of\s*|CI \[[^\]]+\][^\d]{0,4})(\d+) breaks"),
    ("test_a.loo.lo", rf"Leave-one-match-out \(\d+ refits\).{{0,40}}?\[({_NUM}),"),
    ("test_a.loo.hi", rf"Leave-one-match-out \(\d+ refits\).{{0,40}}?\[{_NUM}, ({_NUM})\]"),
    # Perception — denominator and hit rate.
    ("perception.unique_supported", r"(\d+) of \d+ unique claimed breaks"),
    ("perception.unique_total", r"\d+ of (\d+) unique claimed breaks"),
    ("perception.claim_supported", r"(?:\(|claim-level, for comparison, is )(\d+) of \d+"
                                   r"(?: at claim level|\s*\(\d+%\))"),
    ("perception.claim_total", r"(?:\(|claim-level, for comparison, is )\d+ of (\d+)"
                               r"(?: at claim level|\s*\(\d+%\))"),
    ("perception.sweep_with_claims", r"(?:claims on just|attached to just) (\d+) of \d+"
                                     r"(?: randomly)? sampled breaks"),
    ("perception.sweep_n", r"(?:claims on just|attached to just) \d+ of (\d+)"
                           r"(?: randomly)? sampled breaks"),
    ("subs.pct", r"Only ([\d.]+)% of (?:2026 )?second-half substitutions"),
    # Appendix — cards, and the goal-depletion artefact.
    ("cards.w5.D", rf"D = ({_NUM}) / {_NUM} / {_NUM} at the 5 / 8 / 10-minute"),
    ("cards.w8.D", rf"D = {_NUM} / ({_NUM}) / {_NUM} at the 5 / 8 / 10-minute"),
    ("cards.w10.D", rf"D = {_NUM} / {_NUM} / ({_NUM}) at the 5 / 8 / 10-minute"),
    ("cards.goals_real_w8", r"([\d.]+) goals per 8-minute break window against"),
    ("cards.goals_control_w8", r"goals per 8-minute break window against ([\d.]+)"),
    ("cards.n_goals", r"denser than cards \((\d+) vs \d+\)"),
    ("cards.n_cards", r"denser than cards \(\d+ vs (\d+)\)"),
    # Test B directional — sample sizes and effects.
    ("test_b.w5.breaks", r"(?:\(|only )(\d+) / \d+ / \d+ (?:at the 5 / 8 / 10-minute "
                         r"windows|of 203 breaks qualify)"),
    ("test_b.w8.breaks", r"(?:\(|only )\d+ / (\d+) / \d+ (?:at the 5 / 8 / 10-minute "
                         r"windows|of 203 breaks qualify)"),
    ("test_b.w10.breaks", r"(?:\(|only )\d+ / \d+ / (\d+) (?:at the 5 / 8 / 10-minute "
                          r"windows|of 203 breaks qualify)"),
    ("test_b.w5.D", rf"D = ({_NUM}) / {_NUM} / {_NUM}, every interval"),
    ("test_b.w8.D", rf"D = {_NUM} / ({_NUM}) / {_NUM}, every interval"),
    ("test_b.w10.D", rf"D = {_NUM} / {_NUM} / ({_NUM}), every interval"),
    # The support-sensitivity drift — the honest weak point, quoted in both docs.
    ("test_a.primary.effect", rf"steadily more negative \(({_NUM}) → {_NUM} → {_NUM} → {_NUM}\)"),
    ("test_a.min3.effect", rf"steadily more negative \({_NUM} → ({_NUM}) → {_NUM} → {_NUM}\)"),
    ("test_a.min5.effect", rf"steadily more negative \({_NUM} → {_NUM} → ({_NUM}) → {_NUM}\)"),
    ("test_a.min10.effect", rf"steadily more negative \({_NUM} → {_NUM} → {_NUM} → ({_NUM})\)"),
    ("test_a.min10.breaks", r"rests on (\d+) breaks in"),
]

# A check that never matches is a check that cannot fail. Each document must
# exercise at least this many distinct facts, or the patterns have rotted.
MIN_CHECKS = {"README.md": 22, "reports/final/REPORT.md": 25}


def lookup(facts: dict, path: str):
    cur = facts
    for part in path.split("."):
        cur = cur[int(part)] if part.isdigit() else cur[part]
    return cur


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


def sheet(f: dict) -> str:
    """Human-readable fact sheet — the article is written from this file."""
    ta, tb, e, cl = f["test_a"], f["test_b"], f["e1"], f["clock"]
    p, s, cm = f["perception"], f["subs"], f["commercial"]
    L = [
        "# FACT SHEET — every number the prose is allowed to quote",
        "",
        f"Generated {f['generated']} by `python -m src.facts` from the tables in",
        "`reports/tables/`. **Do not re-type numbers into prose from anywhere else.**",
        "`tests/test_report_sync.py` fails the build when a document disagrees with this.",
        "",
        "## The primary sample",
        "",
        f"> {f['primary_sample_note']}",
        "",
        "## 1. Test A — primary matched counterfactual (balance disruption, w=8)",
        "",
        "| variant | breaks | matches | effect | 95% CI (match-clustered) | excludes 0 |",
        "|---|---|---|---|---|---|",
    ]
    for k, lbl in [("primary", "**PRIMARY — Test A**"), ("min3", "≥3 controls"),
                   ("min5", "≥5 controls"), ("min10", "≥10 controls")]:
        r = ta[k]
        L.append(f"| {lbl} | {r['breaks']} | {r['matches']} | {r['effect']:+.3f} | "
                 f"[{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] | "
                 f"{'YES' if r['excludes_zero'] else 'no'} |")
    L += [
        "",
        f"Leave-one-match-out range [{ta['loo']['lo']:+.3f}, {ta['loo']['hi']:+.3f}] "
        f"across {ta['loo']['refits']} refits.",
        "",
        "**Sayable:** no detectable difference from comparable ordinary minutes.",
        "**Not sayable:** robust across all specifications — the support sensitivity "
        f"drifts to {ta['min10']['effect']:+.3f} on {ta['min10']['breaks']} selected breaks.",
        "",
        "## 2. The clock artifact",
        "",
        "| clock | w | observed P(shot) | null |",
        "|---|---|---|---|",
    ]
    for ck in ("display", "adjusted"):
        for w in (5, 8, 10):
            r = cl[f"{ck}_w{w}"]
            L.append(f"| {ck} | {w} | {r['observed']:.3f} | {r['null']:.3f} |")
    L += [
        "",
        f"Headline contrast at w=8: display **{cl['display_w8']['observed']:.3f}** vs "
        f"break-adjusted **{cl['adjusted_w8']['observed']:.3f}** against a null of "
        f"{cl['adjusted_w8']['null']:.3f}.",
        "",
        "## 3. Test B — directional (did the attacking side lose its edge?)",
        "",
        "| w | breaks | matches | swing real | swing matched | D | 95% CI |",
        "|---|---|---|---|---|---|---|",
    ]
    for w in (5, 8, 10):
        r = tb[f"w{w}"]
        L.append(f"| {w} | {r['breaks']} | {r['matches']} | {r['swing_real']:+.3f} | "
                 f"{r['swing_control']:+.3f} | {r['D']:+.3f} | "
                 f"[{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] |")
    L += [
        "",
        interval_sentence([tb[f"w{w}"]["ci"] for w in (5, 8, 10)], "Test B"),
        "",
        "## 4. E1 — clock decomposition (EXPLORATORY, common support "
        f"{e['common_support_breaks']} breaks / {e['common_support_matches']} matches)",
        "",
        "| w | D | 95% CI | A (real − synthetic) | 95% CI |",
        "|---|---|---|---|---|",
    ]
    for w in (3, 5, 8, 10):
        d, a = e["D"][f"w{w}"], e["A"][f"w{w}"]
        L.append(f"| {w} | {d['value']:+.3f} | [{d['ci'][0]:+.3f}, {d['ci'][1]:+.3f}] | "
                 f"{a['value']:+.3f} | [{a['ci'][0]:+.3f}, {a['ci'][1]:+.3f}] |")
    L += [
        "",
        interval_sentence([e["D"][f"w{w}"]["ci"] for w in (3, 5, 8, 10)], "E1 D"),
        " ",
        interval_sentence([e["A"][f"w{w}"]["ci"] for w in (3, 5, 8, 10)], "E1 A"),
        "",
        "## 5. Perception",
        "",
        f"- Stratified random sweep: claims on **{p['sweep_with_claims']} of "
        f"{p['sweep_n']} sampled breaks** ({p['sweep_pct']}%, 95% CI "
        f"{p['sweep_ci'][0]}–{p['sweep_ci'][1]}%).",
        f"- Unique claimed breaks supported: **{p['unique_supported']}/"
        f"{p['unique_total']} ({p['unique_pct']}%)** — the citable rate.",
        f"- Claim level: {p['claim_supported']}/{p['claim_total']} ({p['claim_pct']}%).",
        f"- {p['claims_collected']} claims collected, {p['claims_verified']} "
        f"source-verified, on {p['breaks_with_claims']} of 203 breaks.",
        "",
        "## 6. Substitutions",
        "",
        f"- Within ±3' of the own-match break: **{s['at_break']}/{s['h2_total']} = "
        f"{s['pct']}%** of H2 subs.",
        f"- Minute-matched expectation: {s['exp_2018']}% (2018), {s['exp_2022']}% (2022) "
        "— so 2026 is BELOW, not above.",
        f"- Displacement: {s['before_2026']}% in the 3' before the stoppage, "
        f"{s['after_2026']}% in the 3' from the restart.",
        "",
        "## 7. Commercial inventory (arithmetic only — no motive claim)",
        "",
        f"- Recorded: {cm['break_minutes']} min ≈ {cm['break_hours']} hours "
        f"across 203 breaks ({cm['per_match_min']} min per match).",
        f"- Guaranteed by policy: {cm['policy_slots']} slots ≈ "
        f"{cm['policy_hours']} hours tournament-wide.",
        "",
        "## 8. Appendix — yellow cards (weak proxy, not tempo)",
        "",
        "| w | breaks | D | 95% CI |",
        "|---|---|---|---|",
    ]
    for w in (5, 8, 10):
        r = f["cards"][f"w{w}"]
        L.append(f"| {w} | {r['breaks']} | {r['D']:+.4f} | "
                 f"[{r['ci'][0]:+.4f}, {r['ci'][1]:+.4f}] |")
    L += ["", interval_sentence([f["cards"][f"w{w}"]["ci"] for w in (5, 8, 10)], "card"), ""]
    return "\n".join(L) + "\n"


def main():
    f = collect()
    (REPORTS / "facts.json").write_text(json.dumps(f, indent=2), encoding="utf-8")
    (REPORTS / "FACTS.md").write_text(sheet(f), encoding="utf-8")
    print(f"wrote {REPORTS / 'facts.json'} and {REPORTS / 'FACTS.md'}")
    print(f"  primary Test A: {f['test_a']['primary']['breaks']} breaks, "
          f"effect {f['test_a']['primary']['effect']:+.3f}")
    print(f"  E1 common support: {f['e1']['common_support_breaks']} breaks")


if __name__ == "__main__":
    main()
