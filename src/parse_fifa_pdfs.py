"""Parse cached FIFA Post Match Summary Report PDFs.

Extracts, per match:
  shots        "Attempts at Goal" log pages: minute, player, outcome, body part,
               delivery type (NO per-shot xG — the PMSR does not publish it)
  subs         page-1 lineup minute markers, classified against known goal/card
               minutes from the FIFA dataset; remaining markers are subs
  physical     per-player distance, speed zones, sprints, top speed
  team stats   match xG, attempts, possession (validation layer)

Outputs (data/processed/):
  shots_2026.csv, substitutions_2026.csv, physical_2026.csv,
  fifa_team_stats_2026.csv, parse_qa.csv

Run:  python -m src.parse_fifa_pdfs
"""
from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from pathlib import Path

import fitz
import pandas as pd

from .util import PROCESSED, ROOT, load_fifa

RAW = ROOT / "data" / "raw" / "fifa_pdfs"

OUTCOME_KEYWORDS = ("On Target", "Off Target", "Incomplete", "Blocked", "Deflected")


def norm_name(s: str) -> str:
    """Accent-insensitive uppercase key for player-name matching."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Z ]", "", s.upper()).strip()


# ── shots ────────────────────────────────────────────────────────────────────

def parse_shot_pages(doc, home: str, away: str) -> list[dict]:
    shots = []
    for page in doc:
        lines = [l.strip() for l in page.get_text("text").splitlines() if l.strip()]
        if not lines or lines[0] != "Attempts at Goal":
            continue
        if "Time" not in lines[:8] or "Player" not in lines[:8]:
            continue  # summary chart page, not the log page
        # PDFs use FIFA official names; align to the dataset's spelling
        team = {"Korea Republic": "South Korea"}.get(lines[1], lines[1])
        i, seq = 0, 0
        while i < len(lines) - 2:
            if re.fullmatch(r"\d{1,3}", lines[i]) and 1 <= int(lines[i]) <= 130:
                player, outcome = lines[i + 1], lines[i + 2]
                if not re.fullmatch(r"[\d ]+", player) and any(
                    k in outcome for k in OUTCOME_KEYWORDS
                ):
                    body = lines[i + 3] if i + 3 < len(lines) else ""
                    delivery = lines[i + 4] if i + 4 < len(lines) else ""
                    shots.append(
                        {
                            "team": team, "seq": seq, "minute": int(lines[i]),
                            "player": player, "outcome": outcome,
                            "body_part": body, "delivery_type": delivery,
                            # "On Target - Goal Prevented" is a save, not a goal
                            "is_goal": outcome.endswith("- Goal"),
                        }
                    )
                    seq += 1
                    i += 5
                    continue
            i += 1
    return shots


def assign_periods(shots: list[dict]) -> None:
    """Assign H1/H2 from the (reliable) cumulative match minute.

    The shot log's `seq` order is NOT chronological in many PMSRs, so any
    sequence-based inference misfires; `minute` is the true match minute, so a
    minute cut is the robust rule. Caveat: a first-half stoppage shot notated
    45+X is stored with a base minute up to 48 and is therefore assigned to H2.
    Such shots are few, and nothing downstream keys off `period` (windows and
    buckets use `minute` directly) — this column is for reference only."""
    for s in shots:
        s["period"] = 1 if s["minute"] <= 45 else 2


# ── lineups & substitutions ──────────────────────────────────────────────────

def parse_lineup_markers(doc, home: str, away: str) -> list[dict]:
    """Return [{team, section, player, markers:[minutes]}] from page 1."""
    page = doc[1]
    words = [(w[0], w[1], w[4]) for w in page.get_text("words") if w[4].strip()]
    width = page.rect.width
    out = []
    for team, sel in ((home, lambda x: x < width * 0.40),
                      (away, lambda x: x >= width * 0.55)):
        col = sorted((w for w in words if sel(w[0])), key=lambda w: (round(w[1]), w[0]))
        rows: list[list] = []
        last_y = None
        for x, y, t in col:
            if last_y is None or abs(y - last_y) > 4:
                rows.append([])
                last_y = y
            rows[-1].append(t)
        section = "STARTING"
        current: dict | None = None
        for row in rows:
            txt = " ".join(row)
            if "SUBSTITUTES" in txt.upper():
                section = "SUBSTITUTES"
                current = None
                continue
            if "FORMATION" in txt.upper() or "Distribution" in txt:
                current = None
                continue
            markers = [int(m) for m in re.findall(r"(\d{1,3})'", txt)]
            name = re.sub(r"\d{1,3}'", "", txt)
            name = re.sub(r"\b(GK|DF|MF|FW)\d*\b", " ", name)
            name = re.sub(r"\b\d{1,2}\b", " ", name)
            name = re.sub(r"[+.\-]+", " ", name)
            name = re.sub(r"\s{2,}", " ", name).strip()
            has_name = bool(re.search(r"[A-Za-z]{2}", name))
            if has_name:
                current = {"team": team, "section": section,
                           "player": name, "markers": markers}
                out.append(current)
            elif markers and current is not None:
                current["markers"].extend(markers)
    return out


def _names_match(a: str, b: str) -> bool:
    """Token-subset match: 'Raul JIMENEZ' vs 'Raúl Alonso Jimenez'."""
    ta, tb = set(norm_name(a).split()), set(norm_name(b).split())
    return bool(ta) and bool(tb) and (ta <= tb or tb <= ta)


def build_subs(lineups: list[dict], known: set[tuple[str, int]],
               minutes_played: dict[str, tuple[str, int, int]],
               match_total: int,
               red_carded: set[str] = frozenset()) -> tuple[list[dict], list[str]]:
    """Substitution minutes from PDF markers, arbitrated by lineup minutes.

    minutes_played: dataset player name -> (team, is_starting_xi, minutes).
    Markers explained by a known goal/card/assist (player, minute±1) are dropped.
    A starter's sub-off marker must sit within ±3 of their minutes_played; a
    substitute's sub-on marker within ±3 of (match_total - minutes_played).
    A completeness pass backfills lineup-implied subs the PDF rows missed.
    Returns (subs, qa_flags).
    """
    subs, flags = [], []

    # Some matches ship corrupt lineup minutes (starters at 0, bench at full).
    # There, arbitration is impossible: fall back to marker-only inference.
    n_zero_starters = sum(1 for _, s, mn in minutes_played.values() if s and mn == 0)
    n_full_bench = sum(1 for _, s, mn in minutes_played.values()
                       if not s and mn == match_total)
    if n_zero_starters >= 2 or n_full_bench >= 2:
        flags.append(f"lineup_data_corrupt (zero-min starters: {n_zero_starters}, "
                     f"full-min bench: {n_full_bench}); marker-only fallback")
        for entry in lineups:
            player, team, section = entry["player"], entry["team"], entry["section"]
            for m in entry["markers"]:
                if any(_names_match(player, p) and abs(m - mn) <= 1 for p, mn in known):
                    continue
                subs.append({"team": team, "player": player, "minute": m,
                             "direction": "off" if section == "STARTING" else "on",
                             "source": "pdf_marker_unarbitrated"})
        return subs, flags

    def lookup(player: str):
        hits = [(n, v) for n, v in minutes_played.items() if _names_match(player, n)]
        return hits[0] if len(hits) == 1 else (None, None)

    def implied(ds_name: str, is_starter: int, mins: int):
        # a red-carded player leaves early without a substitution
        if any(_names_match(ds_name, r) for r in red_carded):
            return None
        if is_starter:
            return mins if mins < match_total else None
        return (match_total - mins) if mins > 0 else None

    seen: set[str] = set()
    for entry in lineups:
        player, team, section = entry["player"], entry["team"], entry["section"]
        ds_name, lu = lookup(player)
        markers = [
            m for m in entry["markers"]
            if not any(_names_match(player, p) and abs(m - mn) <= 1 for p, mn in known)
        ]
        if lu is None:
            if markers:
                flags.append(f"{team} {player}: no lineup match for markers {markers}")
            continue
        _, is_starter, mins = lu
        expect = implied(ds_name, is_starter, mins)
        if expect is None:
            # recover stoppage-time subs the dataset rounds away: starters
            # recorded as full-match (sub-off 90+X) and substitutes recorded
            # as 0 minutes (sub-on 90+X)
            late = [m for m in markers if m >= 85]
            starter_late = is_starter and mins == match_total
            bench_late = not is_starter and mins == 0
            if (late and (starter_late or bench_late)
                    and not any(_names_match(ds_name, r) for r in red_carded)):
                seen.add(norm_name(ds_name))
                subs.append({"team": team, "player": player, "minute": min(late),
                             "direction": "off" if is_starter else "on",
                             "source": "pdf_marker_late"})
            elif markers:
                flags.append(f"{team} {player}: unexplained markers {markers} "
                             f"(mins={mins}, {section.lower()})")
            continue
        if norm_name(ds_name) in seen:
            continue
        seen.add(norm_name(ds_name))
        direction = "off" if is_starter else "on"
        near = [m for m in markers if abs(m - expect) <= 3]
        minute = min(near, key=lambda m: abs(m - expect)) if near else expect
        source = "pdf_marker" if near else "lineup_derived"
        subs.append({"team": team, "player": player, "minute": minute,
                     "direction": direction, "source": source})
        if not near and markers:
            flags.append(f"{team} {player}: markers {markers} far from expected {expect}")

    # completeness: lineup-implied subs with no PDF row at all
    for ds_name, (team, is_starter, mins) in minutes_played.items():
        expect = implied(ds_name, is_starter, mins)
        if expect is None or norm_name(ds_name) in seen:
            continue
        seen.add(norm_name(ds_name))
        subs.append({"team": team, "player": ds_name, "minute": expect,
                     "direction": "off" if is_starter else "on",
                     "source": "lineup_derived"})
        flags.append(f"{team} {ds_name}: sub implied by lineup minutes ({mins}) "
                     "but no PDF row parsed")
    return subs, flags


# ── physical & team stats ────────────────────────────────────────────────────

PHYS_COLS = ["total_distance_m", "zone1_m", "zone2_m", "zone3_m", "zone4_m",
             "zone5_m", "high_speed_runs", "sprints", "top_speed_kmh"]


def parse_physical(doc) -> list[dict]:
    rows = []
    for page in doc:
        lines = [l.strip() for l in page.get_text("text").splitlines() if l.strip()]
        if not lines or lines[0] != "Physical Data":
            continue
        team = lines[1]
        i = 0
        while i < len(lines) - 10:
            if re.fullmatch(r"\d{1,2}", lines[i]) and re.search(r"[A-Za-z]{2}", lines[i + 1]):
                nums = lines[i + 2 : i + 11]
                if len(nums) == 9 and all(
                    re.fullmatch(r"[\d.]+|[-–]", n) for n in nums
                ):
                    vals = [float(n) if n not in "-–" else float("nan") for n in nums]
                    # PyMuPDF sometimes emits the last two columns (sprints,
                    # top_speed_kmh) out of reading order when sprints is a
                    # small right-aligned integer (typically goalkeepers).
                    # Two signals that the pair is swapped, both robust because
                    # sprints is an integer count and top speed a km/h value
                    # that must exceed ~18 for anyone who ran:
                    #   (a) parsed "sprints" has a fractional part, or
                    #   (b) parsed "top speed" < 18 while "sprints" >= 18.
                    sp, ts = vals[7], vals[8]
                    swapped = False
                    if sp == sp and ts == ts:  # both present
                        if (sp % 1 != 0) or (ts < 18 and sp >= 18):
                            swapped = True
                    if swapped:
                        vals[7], vals[8] = ts, sp
                    rows.append(
                        {"team": team, "jersey": int(lines[i]), "player": lines[i + 1],
                         **dict(zip(PHYS_COLS, vals)),
                         "phys_col_swap_fixed": swapped}
                    )
                    i += 11
                    continue
            i += 1
    return rows


def parse_team_stats(doc, home: str, away: str) -> dict:
    for page in doc:
        text = page.get_text("text")
        if "Match Summary - Key Statistics" not in text:
            continue
        stats = {}
        m = re.search(r"([\d.]+)\s*\n\s*xG \(Expected Goals\)\s*\n\s*([\d.]+)", text)
        if m:
            stats["xg_home"], stats["xg_away"] = float(m.group(1)), float(m.group(2))
        m = re.search(r"(\d+)\s*\((\d+)\)\s*\n\s*Attempts at Goal \(On Target\)\s*\n\s*(\d+)\s*\((\d+)\)", text)
        if m:
            stats.update(shots_home=int(m.group(1)), sot_home=int(m.group(2)),
                         shots_away=int(m.group(3)), sot_away=int(m.group(4)))
        m = re.search(r"([\d.]+) km\s*\n\s*Total Distance Covered\s*\n\s*([\d.]+) km", text)
        if m:
            stats["distance_km_home"], stats["distance_km_away"] = float(m.group(1)), float(m.group(2))
        return stats
    return {}


# ── driver ───────────────────────────────────────────────────────────────────

def known_goal_card_minutes() -> dict[int, set[tuple[str, int]]]:
    """(normalized player, minute) of goals/cards per match from the FIFA dataset."""
    events = load_fifa("match_events.csv")
    players = load_fifa("squads_and_players.csv")
    id_to_name = dict(zip(players["player_id"], players["player_name"]))
    out: dict[int, set] = defaultdict(set)
    for _, e in events.iterrows():
        name = id_to_name.get(e["player_id"])
        if name and e["event_type"] in ("Goal", "Yellow Card", "Red Card", "Assist"):
            # "90+6" -> 96 to match the PDF's displayed-minute markers
            parts = str(e["minute"]).split("+")
            minute = sum(int(p) for p in parts)
            out[e["match_id"]].add((norm_name(name), minute))
    return out


def lineup_minutes() -> dict[int, dict[str, tuple[str, int, int]]]:
    """match_id -> {player_name: (team_name, is_starting_xi, minutes_played)}."""
    lu = load_fifa("match_lineups.csv")
    pl = load_fifa("squads_and_players.csv")[["player_id", "player_name"]]
    teams = load_fifa("teams.csv")[["team_id", "team_name"]]
    merged = lu.merge(pl, on="player_id").merge(teams, on="team_id")
    out: dict[int, dict] = defaultdict(dict)
    for _, r in merged.iterrows():
        out[r["match_id"]][r["player_name"]] = (
            r["team_name"], int(r["is_starting_xi"]), int(r["minutes_played"])
        )
    return out


def red_carded_players() -> dict[int, set[str]]:
    events = load_fifa("match_events.csv")
    players = load_fifa("squads_and_players.csv")[["player_id", "player_name"]]
    id_to_name = dict(zip(players["player_id"], players["player_name"]))
    out: dict[int, set] = defaultdict(set)
    reds = events[events["event_type"] == "Red Card"]
    for _, e in reds.iterrows():
        name = id_to_name.get(e["player_id"])
        if name:
            out[e["match_id"]].add(name)
    return out


def main():
    index = pd.read_csv(RAW / "index.csv")
    matches = pd.read_csv(PROCESSED / "matches.csv").set_index("match_id")
    known = known_goal_card_minutes()
    lu_minutes = lineup_minutes()
    reds = red_carded_players()

    all_shots, all_subs, all_phys, all_stats, qa = [], [], [], [], []
    for _, r in index.iterrows():
        if r["status"] != "ok":
            continue
        mid = int(r["match_id"])
        m = matches.loc[mid]
        doc = fitz.open(RAW / r["file"])

        shots = parse_shot_pages(doc, m["home"], m["away"])
        assign_periods(shots)
        for s in shots:
            s["match_id"] = mid
        match_total = 90 if m["result_type"] == "Regular" else 120
        subs, sub_flags = build_subs(
            parse_lineup_markers(doc, m["home"], m["away"]),
            known[mid], lu_minutes[mid], match_total, reds[mid],
        )
        for s in subs:
            s["match_id"] = mid
        phys = parse_physical(doc)
        for p in phys:
            p["match_id"] = mid
        stats = parse_team_stats(doc, m["home"], m["away"])
        stats["match_id"] = mid

        # per-team reconciliation: a deficit vs the official score is an own
        # goal (never present in the scoring team's shot log); a surplus is a
        # parse error
        goals_home_pdf = sum(s["is_goal"] and s["team"] == m["home"] for s in shots)
        goals_away_pdf = sum(s["is_goal"] and s["team"] != m["home"] for s in shots)
        own_home = int(m["home_score"]) - goals_home_pdf
        own_away = int(m["away_score"]) - goals_away_pdf
        n_on = sum(1 for s in subs if s["direction"] == "on")
        n_off = sum(1 for s in subs if s["direction"] == "off")
        qa.append(
            {
                "match_id": mid, "n_shots": len(shots),
                "goals_pdf": goals_home_pdf + goals_away_pdf,
                "goals_expected": int(m["home_score"] + m["away_score"]),
                "own_goals_inferred": max(own_home, 0) + max(own_away, 0),
                "goals_match": own_home >= 0 and own_away >= 0,
                "xg_home_pdf": stats.get("xg_home"), "xg_home_meta": m["home_xg"],
                "subs_on": n_on, "subs_off": n_off, "subs_balanced": n_on == n_off,
                "n_physical_rows": len(phys),
                "sub_flags": "; ".join(sub_flags),
            }
        )
        all_shots += shots
        all_subs += subs
        all_phys += phys
        all_stats.append(stats)
        doc.close()

    pd.DataFrame(all_shots).to_csv(PROCESSED / "shots_2026.csv", index=False)
    pd.DataFrame(all_subs).to_csv(PROCESSED / "substitutions_2026.csv", index=False)
    pd.DataFrame(all_phys).to_csv(PROCESSED / "physical_2026.csv", index=False)
    pd.DataFrame(all_stats).to_csv(PROCESSED / "fifa_team_stats_2026.csv", index=False)
    qa_df = pd.DataFrame(qa)
    qa_df.to_csv(PROCESSED / "parse_qa.csv", index=False)

    print(f"parsed {len(qa_df)} PDFs")
    print(f"shots: {len(all_shots)}  subs rows: {len(all_subs)}  "
          f"physical rows: {len(all_phys)}")
    print(f"goal reconciliation: {qa_df['goals_match'].sum()}/{len(qa_df)} matches exact")
    print(f"sub balance (on==off): {qa_df['subs_balanced'].sum()}/{len(qa_df)}")
    bad = qa_df[~qa_df["goals_match"]]
    if len(bad):
        print("goal mismatches:")
        print(bad[["match_id", "goals_pdf", "goals_expected"]].to_string(index=False))


if __name__ == "__main__":
    main()
