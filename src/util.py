"""Shared paths, loaders and the SofaScore->FIFA match-ID mapping."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external"
HYD = EXTERNAL / "wc2026-hydration-momentum"
FIFA = EXTERNAL / "FIFA-World-Cup-2026-Dataset"
ANALYTICS = EXTERNAL / "wc26-analytics"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
TABLES = REPORTS / "tables"

# Hydration-repo spelling -> FIFA-dataset spelling
TEAM_NAME_MAP = {
    "Bosnia & Herzegovina": "Bosnia and Herzegovina",
    "DR Congo": "Congo DR",
    "Iran": "IR Iran",
}


def norm_team(name: str) -> str:
    return TEAM_NAME_MAP.get(name, name)


def excludes_zero(lo: float, hi: float) -> bool:
    return lo > 0 or hi < 0


def interval_sentence(intervals, subject: str) -> str:
    """Describe a set of confidence intervals — GENERATED, never hard-coded.

    Hand-written versions of this sentence went false three separate times while
    sitting directly beside a table that disproved them. Every module that wants
    to summarise a column of intervals must call this, and
    tests/test_report_sync.py fails the build on any universal claim that the
    numbers contradict.
    """
    intervals = [tuple(iv) for iv in intervals]
    bad = [iv for iv in intervals if excludes_zero(*iv)]
    if not bad:
        return f"**Every {subject} interval includes zero.**"
    if len(bad) == len(intervals):
        return f"**Every {subject} interval excludes zero.**"
    return (f"**{len(bad)} of {len(intervals)} {subject} intervals exclude zero**"
            f" ({', '.join(f'[{lo:+.3f}, {hi:+.3f}]' for lo, hi in bad)});"
            f" the remainder include it.")


def load_json(path: Path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_hyd():
    """All shipped hydration-repo data files."""
    d = HYD / "data"
    return {
        "treated": load_json(d / "treated_covariates.json"),
        "controls": load_json(d / "control_candidates_all.json"),
        "break_exact": load_json(d / "break_times_exact.json"),
        "manifest": load_json(d / "manifest.json"),
        "gv": load_json(d / "_gv.json"),
    }


def load_fifa(name: str) -> pd.DataFrame:
    return pd.read_csv(FIFA / name, encoding="utf-8-sig")


def sofascore_match_index() -> pd.DataFrame:
    """One row per SofaScore match id with kickoff ts (UTC) and team names.

    Group matches: ids + teams from manifest['wc2026_group_momentum.json'],
    kickoff ts from _gv.json. Knockout matches carry their own ts.
    """
    hyd = load_hyd()
    gv_ts = {g["id"]: g for g in hyd["gv"]}
    rows = []
    for g in hyd["manifest"]["wc2026_group_momentum.json"]:
        ts = gv_ts.get(g["id"], {}).get("ts")
        rows.append(
            {
                "sofascore_id": g["id"],
                "stage_type": "group",
                "home": norm_team(g["home"]),
                "away": norm_team(g["away"]),
                "kickoff_ts": ts,
                "home_score": g["hs"],
                "away_score": g["as"],
            }
        )
    for g in hyd["manifest"]["wc2026_knockout_raw.json"]:
        rows.append(
            {
                "sofascore_id": g["id"],
                "stage_type": "knockout",
                "home": norm_team(g["home"]),
                "away": norm_team(g["away"]),
                "kickoff_ts": g.get("ts"),
                "home_score": g["hs"],
                "away_score": g["as"],
            }
        )
    df = pd.DataFrame(rows)
    df["kickoff_utc"] = df["kickoff_ts"].map(
        lambda t: datetime.fromtimestamp(t, tz=timezone.utc) if pd.notna(t) else pd.NaT
    )
    return df


def fifa_match_index() -> pd.DataFrame:
    """FIFA matches.csv joined with team names, stage names and venue geo."""
    matches = load_fifa("matches.csv")
    teams = load_fifa("teams.csv")[["team_id", "team_name"]]
    stages = load_fifa("tournament_stages.csv")[["stage_id", "stage_name"]]
    venues = load_fifa("venues.csv")

    df = (
        matches.merge(teams.rename(columns={"team_id": "home_team_id", "team_name": "home"}), on="home_team_id")
        .merge(teams.rename(columns={"team_id": "away_team_id", "team_name": "away"}), on="away_team_id")
        .merge(stages, on="stage_id")
        .merge(venues, on="venue_id")
    )
    df["kickoff_dt_utc"] = pd.to_datetime(df["date"] + " " + df["kickoff_time_utc"], utc=True)
    return df


def build_id_map() -> pd.DataFrame:
    """Map sofascore_id -> FIFA match_id via unordered team pair + closest kickoff.

    Requires kickoff dates to agree within 1 day; team pairs disambiguate the rest.
    """
    sofa = sofascore_match_index()
    fifa = fifa_match_index()
    fifa_by_pair: dict[frozenset, list] = {}
    for _, r in fifa.iterrows():
        fifa_by_pair.setdefault(frozenset((r["home"], r["away"])), []).append(r)

    out = []
    for _, s in sofa.iterrows():
        cands = fifa_by_pair.get(frozenset((s["home"], s["away"])), [])
        best, best_gap = None, None
        for c in cands:
            if pd.isna(s["kickoff_utc"]):
                gap = 0 if len(cands) == 1 else None
            else:
                gap = abs((c["kickoff_dt_utc"] - s["kickoff_utc"]).total_seconds())
            if gap is not None and (best_gap is None or gap < best_gap):
                best, best_gap = c, gap
        out.append(
            {
                "sofascore_id": s["sofascore_id"],
                "match_id": None if best is None else int(best["match_id"]),
                "kickoff_gap_hours": None if best_gap is None else round(best_gap / 3600, 2),
                "home": s["home"],
                "away": s["away"],
            }
        )
    return pd.DataFrame(out)
