"""Extract WC 2018 / WC 2022 baselines from StatsBomb open data.

Outputs (data/processed/):
  historical_subs.csv         one row per substitution, with score state
  historical_match_times.csv  one row per match: half end times (added time), ET flag
  historical_goals.csv        one row per goal (incl. own goals), display minute

Run:  python -m src.statsbomb_extract
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .util import EXTERNAL, PROCESSED

SB = EXTERNAL / "statsbomb-open-data" / "data"
SEASONS = {"3": "WC2018", "106": "WC2022"}


def load_matches() -> pd.DataFrame:
    rows = []
    for season_id, label in SEASONS.items():
        with open(SB / "matches" / "43" / f"{season_id}.json", encoding="utf-8") as f:
            for m in json.load(f):
                rows.append(
                    {
                        "tournament": label,
                        "match_id": m["match_id"],
                        "date": m["match_date"],
                        "stage": m["competition_stage"]["name"],
                        "home": m["home_team"]["home_team_name"],
                        "away": m["away_team"]["away_team_name"],
                        "home_score": m["home_score"],
                        "away_score": m["away_score"],
                    }
                )
    return pd.DataFrame(rows)


def extract(matches: pd.DataFrame):
    subs, times, goals = [], [], []
    for _, m in matches.iterrows():
        with open(SB / "events" / f"{m.match_id}.json", encoding="utf-8") as f:
            events = json.load(f)

        goal_events = []
        for e in events:
            t = e["type"]["name"]
            if t == "Shot" and e.get("shot", {}).get("outcome", {}).get("name") == "Goal":
                goal_events.append((e["minute"], e["second"], e["team"]["name"], "goal", e["period"]))
            elif t == "Own Goal Against":
                # credited against e['team']; scoring team is the opponent
                scorer = m.home if e["team"]["name"] == m.away else m.away
                goal_events.append((e["minute"], e["second"], scorer, "own_goal", e["period"]))
        goal_events.sort()
        for minute, second, team, kind, period in goal_events:
            goals.append(
                {
                    "tournament": m.tournament, "match_id": m.match_id, "stage": m.stage,
                    "period": period, "minute": minute, "second": second,
                    "team": team, "kind": kind,
                }
            )

        def score_at(minute, second, team):
            f = sum(1 for mn, sc, tm, _, _ in goal_events
                    if tm == team and (mn, sc) < (minute, second))
            a = sum(1 for mn, sc, tm, _, _ in goal_events
                    if tm != team and (mn, sc) < (minute, second))
            return f, a

        sub_count: dict[str, int] = {}
        for e in events:
            t = e["type"]["name"]
            if t == "Substitution":
                team = e["team"]["name"]
                sub_count[team] = sub_count.get(team, 0) + 1
                f, a = score_at(e["minute"], e["second"], team)
                subs.append(
                    {
                        "tournament": m.tournament, "match_id": m.match_id,
                        "date": m.date, "stage": m.stage,
                        "team": team,
                        "opponent": m.away if team == m.home else m.home,
                        "period": e["period"], "minute": e["minute"], "second": e["second"],
                        "player_out": e["player"]["name"],
                        "player_in": e["substitution"]["replacement"]["name"],
                        "sub_reason": e["substitution"].get("outcome", {}).get("name"),
                        "sub_number_for_team": sub_count[team],
                        "score_for": f, "score_against": a,
                        "score_state": "leading" if f > a else ("trailing" if f < a else "level"),
                    }
                )

        period_end: dict[int, tuple[int, int]] = {}
        for e in events:
            if e["type"]["name"] == "Half End":
                p = e["period"]
                cur = (e["minute"], e["second"])
                period_end[p] = max(period_end.get(p, (0, 0)), cur)
        times.append(
            {
                "tournament": m.tournament, "match_id": m.match_id, "stage": m.stage,
                "home": m.home, "away": m.away,
                "home_score": m.home_score, "away_score": m.away_score,
                "h1_end_minute": period_end.get(1, (None,))[0],
                "h2_end_minute": period_end.get(2, (None,))[0],
                "went_to_extra_time": 3 in period_end,
                "et1_end_minute": period_end.get(3, (None,))[0],
                "et2_end_minute": period_end.get(4, (None,))[0],
            }
        )
    return pd.DataFrame(subs), pd.DataFrame(times), pd.DataFrame(goals)


def main():
    matches = load_matches()
    subs, times, goals = extract(matches)
    subs.to_csv(PROCESSED / "historical_subs.csv", index=False)
    times.to_csv(PROCESSED / "historical_match_times.csv", index=False)
    goals.to_csv(PROCESSED / "historical_goals.csv", index=False)

    print(f"matches: {len(matches)} ({matches.groupby('tournament').size().to_dict()})")
    print(f"subs: {len(subs)} ({subs.groupby('tournament').size().to_dict()})")
    print(f"goals: {len(goals)} ({goals.groupby('tournament').size().to_dict()})")
    print("\nmean added time (displayed end minute):")
    reg = times
    print(reg.groupby("tournament")[["h1_end_minute", "h2_end_minute"]].mean().round(2).to_string())
    print("\nsubs in minutes 60-75 share:")
    in_window = subs[(subs["period"] == 2) & subs["minute"].between(60, 75)]
    share = in_window.groupby("tournament").size() / subs.groupby("tournament").size()
    print(share.round(3).to_string())


if __name__ == "__main__":
    main()
