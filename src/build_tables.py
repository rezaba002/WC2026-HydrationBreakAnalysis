"""Build the Milestone-1 master tables.

Outputs (data/processed/):
  matches.csv          104 rows — FIFA backbone + venue geo + sofascore id + treated flags
  venues.csv           16 rows
  breaks.csv           ~203 rows — treated breaks enriched with manifest/commentary timing
  exclusions.csv       documented gaps, never hidden
  source_coverage.csv  per-match availability of each data field per source

Run:  python -m src.build_tables
"""
from __future__ import annotations

import pandas as pd

from .util import PROCESSED, build_id_map, fifa_match_index, load_fifa, load_hyd

pd.set_option("display.width", 200)


def build_matches(id_map: pd.DataFrame, hyd) -> pd.DataFrame:
    fifa = fifa_match_index()
    treated_ids = {r["match_id"] for r in hyd["treated"]}
    n_breaks = pd.Series([r["match_id"] for r in hyd["treated"]]).value_counts()

    df = fifa.merge(id_map[["sofascore_id", "match_id", "kickoff_gap_hours"]], on="match_id", how="left")
    df["in_treated"] = df["sofascore_id"].isin(treated_ids)
    df["n_treated_breaks"] = df["sofascore_id"].map(n_breaks).fillna(0).astype(int)

    cols = [
        "match_id", "sofascore_id", "date", "kickoff_time_utc", "stage_name",
        "home", "away", "home_score", "away_score", "result_type",
        "home_penalty_score", "away_penalty_score", "home_xg", "away_xg",
        "venue_id", "stadium_name", "city", "country", "latitude", "longitude",
        "elevation_meters", "referee_id", "in_treated", "n_treated_breaks",
        "kickoff_gap_hours",
    ]
    out = df[cols].sort_values("match_id").reset_index(drop=True)
    return out


def build_breaks(id_map: pd.DataFrame, hyd) -> pd.DataFrame:
    sofa_to_fifa = dict(zip(id_map["sofascore_id"], id_map["match_id"]))

    # displayed-clock break bands from the group manifest (start/end).
    # Some entries list the bands out of order, so assign by minute: a band
    # starting before 45' is the first-half break, otherwise second-half.
    manifest_breaks: dict[tuple[int, int], dict] = {}
    for g in hyd["manifest"]["wc2026_group_momentum.json"]:
        for b in g.get("breaks", []):
            manifest_breaks[(g["id"], 1 if b["start"] < 45 else 2)] = b

    # commentary-derived exact minutes, knockout only
    exact = {e["id"]: e for e in hyd["break_exact"]}

    rows = []
    for r in hyd["treated"]:
        break_number = 1 if r["half"] == "H1" else 2
        mb = manifest_breaks.get((r["match_id"], break_number))
        ex = exact.get(r["match_id"])
        commentary_minute = ex["breakMins"][break_number - 1] if ex else None
        manifest_start = mb["start"] if mb else None
        manifest_end = mb["end"] if mb else None

        sources = [m for m in (manifest_start, commentary_minute) if m is not None]
        timing_consistent = all(m == r["minute"] for m in sources) if sources else None

        # Manifest end minutes are noisy: some bands are zero-length or span
        # both halves. Trust the duration only when it is 1-6 minutes;
        # otherwise keep the start and flag the band.
        duration = None
        band_quality = "no_band"
        if mb is not None:
            duration = manifest_end - manifest_start
            if 1 <= duration <= 6:
                band_quality = "ok"
            else:
                band_quality = "implausible_end"
                duration = None

        rows.append(
            {
                "match_id": sofa_to_fifa.get(r["match_id"]),
                "sofascore_id": r["match_id"],
                "break_number": break_number,
                "half": r["half"],
                "stage": r["stage"],
                "start_minute": r["minute"],
                "manifest_start": manifest_start,
                "manifest_end": manifest_end,
                "duration_display_min": duration,
                "band_quality": band_quality,
                "commentary_minute": commentary_minute,
                "n_commentary": ex["nCom"] if ex else None,
                "timing_consistent": timing_consistent,
                "margin": r["margin"],
                "leadside": r["leadside"],
                "orient": r["orient"],
                "pre_level": r["pre_level"],
                "pre_slope": r["pre_slope"],
                "post_level": r["post_level"],
                "wbgt": r["wbgt"],
                "tempC": r.get("tempC"),
                "local_hour": r["local_hour"],
                "elo_home": r.get("elo_home"),
                "elo_away": r.get("elo_away"),
                "elo_gap_or": r.get("elo_gap_or"),
                "unit": r["unit"],
            }
        )
    df = pd.DataFrame(rows).sort_values(["match_id", "break_number"]).reset_index(drop=True)
    return df


def build_exclusions(matches: pd.DataFrame, hyd) -> pd.DataFrame:
    rows = []
    unmapped = matches[matches["sofascore_id"].isna()]
    for _, m in unmapped.iterrows():
        rows.append(
            {
                "entity": "match",
                "match_id": m["match_id"],
                "sofascore_id": None,
                "home": m["home"],
                "away": m["away"],
                "stage": m["stage_name"],
                "reason": "absent from hydration repo entirely (no manifest entry, no treated rows)",
                "evidence": "no sofascore manifest id matches this fixture",
                "status": "excluded from treated sample; pipeline can add later",
            }
        )
    treated_ids = {r["match_id"] for r in hyd["treated"]}
    mapped = matches[matches["sofascore_id"].notna() & ~matches["in_treated"]]
    for _, m in mapped.iterrows():
        g = next(
            x for x in hyd["manifest"]["wc2026_group_momentum.json"] + hyd["manifest"]["wc2026_knockout_raw.json"]
            if x["id"] == m["sofascore_id"]
        )
        rows.append(
            {
                "entity": "match",
                "match_id": m["match_id"],
                "sofascore_id": m["sofascore_id"],
                "home": m["home"],
                "away": m["away"],
                "stage": m["stage_name"],
                "reason": "manifest entry exists (with break bands) but no treated covariate rows shipped",
                "evidence": f"manifest breaks: {g.get('breaks')}",
                "status": "excluded from treated sample; cause unknown (likely missing momentum arrays)",
            }
        )
    # halves with no recorded break inside treated matches
    by_match: dict[int, list] = {}
    for r in hyd["treated"]:
        by_match.setdefault(r["match_id"], []).append(r["half"])
    for sid, halves in by_match.items():
        for half in ("H1", "H2"):
            if half not in halves:
                m = matches[matches["sofascore_id"] == sid].iloc[0]
                g = next(
                    x for x in hyd["manifest"]["wc2026_group_momentum.json"] + hyd["manifest"]["wc2026_knockout_raw.json"]
                    if x["id"] == sid
                )
                rows.append(
                    {
                        "entity": "half",
                        "match_id": m["match_id"],
                        "sofascore_id": sid,
                        "home": m["home"],
                        "away": m["away"],
                        "stage": m["stage_name"],
                        "reason": f"no {half} hydration break recorded in any shipped source",
                        "evidence": f"treated halves: {sorted(halves)}; manifest breaks: {g.get('breaks')}",
                        "status": "consistent across shipped sources; REQUIRES independent external verification",
                    }
                )
    return pd.DataFrame(rows)


def build_coverage(matches: pd.DataFrame, breaks: pd.DataFrame, hyd) -> pd.DataFrame:
    events = load_fifa("match_events.csv")
    lineups = load_fifa("match_lineups.csv")
    stats = load_fifa("match_team_stats.csv")
    goal_ids = set(events.loc[events["event_type"] == "Goal", "match_id"])
    lineup_ids = set(lineups["match_id"])
    stats_ids = set(stats["match_id"])
    exact_ids = {e["id"] for e in hyd["break_exact"]}
    ko_manifest = {g["id"]: g for g in hyd["manifest"]["wc2026_knockout_raw.json"]}
    grp_manifest = {g["id"]: g for g in hyd["manifest"]["wc2026_group_momentum.json"]}
    breaks_by_fifa = breaks.groupby("match_id").size()

    rows = []
    for _, m in matches.iterrows():
        sid = m["sofascore_id"]
        g = grp_manifest.get(sid) or ko_manifest.get(sid)
        rows.append(
            {
                "match_id": m["match_id"],
                "sofascore_id": sid,
                "meta_fifa": 1,
                "match_level_xg_fifa": int(pd.notna(m["home_xg"])),
                "venue_geo": int(pd.notna(m["latitude"])),
                "lineups_fifa": int(m["match_id"] in lineup_ids),
                "team_stats_fifa": int(m["match_id"] in stats_ids),
                "goals_fifa_events": int(m["match_id"] in goal_ids),
                "goals_manifest": int(bool(g and g.get("goals") is not None)),
                "break_band_manifest": int(bool(g and g.get("breaks"))),
                "break_minute_commentary": int(sid in exact_ids),
                "treated_covariates": int(m["in_treated"]),
                "n_treated_breaks": int(breaks_by_fifa.get(m["match_id"], 0)),
                "wbgt_estimate": int(m["in_treated"]),
                "added_time_manifest": int(bool(g and g.get("injury"))),
                "shot_level_xg": 0,      # Milestone 2: FIFA PDFs / FBref
                "substitution_events": 0,  # Milestone 2: FBref (2026), StatsBomb (2018/22)
                "momentum_minute_level": 0,  # not shipped; SofaScore regeneration needed
            }
        )
    return pd.DataFrame(rows)


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    hyd = load_hyd()
    id_map = build_id_map()

    n_dup = id_map["match_id"].dropna().duplicated().sum()
    print(f"id map: {id_map['match_id'].notna().sum()}/103 sofascore ids mapped, duplicates: {n_dup}")
    print(f"kickoff gap hours: max {id_map['kickoff_gap_hours'].max()}")

    matches = build_matches(id_map, hyd)
    venues = load_fifa("venues.csv")
    breaks = build_breaks(id_map, hyd)
    exclusions = build_exclusions(matches, hyd)
    coverage = build_coverage(matches, breaks, hyd)

    matches.to_csv(PROCESSED / "matches.csv", index=False)
    venues.to_csv(PROCESSED / "venues.csv", index=False)
    breaks.to_csv(PROCESSED / "breaks.csv", index=False)
    exclusions.to_csv(PROCESSED / "exclusions.csv", index=False)
    coverage.to_csv(PROCESSED / "source_coverage.csv", index=False)

    print(f"\nmatches.csv:   {len(matches)} rows ({matches['in_treated'].sum()} treated)")
    print(f"venues.csv:    {len(venues)} rows")
    print(f"breaks.csv:    {len(breaks)} rows "
          f"(H1: {(breaks['half'] == 'H1').sum()}, H2: {(breaks['half'] == 'H2').sum()})")
    print(f"timing_consistent: {breaks['timing_consistent'].value_counts(dropna=False).to_dict()}")
    print(f"exclusions.csv: {len(exclusions)} rows")
    print(exclusions[["entity", "match_id", "home", "away", "reason"]].to_string(index=False))
    print(f"source_coverage.csv: {len(coverage)} rows")


if __name__ == "__main__":
    main()
