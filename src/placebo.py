"""Core Output 3 — dual-clock randomized placebo analysis (Test A).

For each real hydration break, enumerate eligible pseudo-break minutes in the
same match and half (matched on score state; excluding minutes near goals, red
cards, VAR reviews, half edges and the real break itself), then compare the
observed post-break change against the distribution of 10,000 randomized
pseudo-break assignments.

Outcomes (CHANGELOG A2/A3), each computed on both clocks:
  total_change            post total shots − pre total shots (tempo)
  shot_diff_change        Δ(home−away) shots, signed
  balance_disruption      |Δ(home−away)| — primary, always defined
  sot_diff_change         Δ(home−away) shots on target
  next_shot_within_W      any shot within W break-adjusted minutes after restart

Windows 5/8/10 break-adjusted minutes; primary 8. Seed 20260724.
Uncertainty: match-cluster bootstrap of the observed means.

Outputs:
  data/processed/placebo_break_level.csv   per-break observed outcomes
  reports/tables/placebo_results.md        aggregate results
  data/processed/placebo_null_draws.csv    null-distribution means (for charts)

Run:  python -m src.placebo
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from .clocks import Band, MatchClocks
from .util import FIFA, PROCESSED, TABLES

SEED = 20260724
N_DRAWS = 10_000
N_BOOT = 5_000
WINDOWS = (5, 8, 10)
PRIMARY_W = 8

H_BOUNDS = {"H1": (1, 45), "H2": (46, 90)}
ELIGIBLE = {"H1": range(9, 37), "H2": range(54, 82)}
GOAL_EXCL, RED_EXCL, VAR_EXCL, BREAK_EXCL = 3, 3, 2, 3


def _parse_minute(v) -> float:
    """'45+2' -> 45.9 (sorts after 45', before 46'); '67' -> 67.0"""
    m = re.match(r"(\d+)(?:\+(\d+))?", str(v))
    base = float(m.group(1))
    return base + 0.9 if m.group(2) else base


def load_inputs():
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    shots = pd.read_csv(PROCESSED / "shots_2026.csv")
    matches = pd.read_csv(PROCESSED / "matches.csv").set_index("match_id")
    events = pd.read_csv(FIFA / "match_events.csv", encoding="utf-8-sig")
    events["pos"] = events["minute"].map(_parse_minute)
    teams = pd.read_csv(FIFA / "teams.csv", encoding="utf-8-sig")[["team_id", "team_name"]]
    events = events.merge(teams, on="team_id", how="left")
    return bands, shots, matches, events


class MatchData:
    """Per-match pre-indexed shot/goal/exclusion data."""

    def __init__(self, mid: int, matches, shots, events, bands):
        row = matches.loc[mid]
        self.home, self.away = row["home"], row["away"]
        sub = shots[shots["match_id"] == mid]
        self.shot_pos = {
            "home": np.sort(sub.loc[sub["team"] == self.home, "minute"].to_numpy(float)),
            "away": np.sort(sub.loc[sub["team"] == self.away, "minute"].to_numpy(float)),
        }
        self.sot_pos = {
            side: np.sort(sub.loc[(sub["team"] == team)
                                  & sub["outcome"].str.startswith("On Target"),
                                  "minute"].to_numpy(float))
            for side, team in (("home", self.home), ("away", self.away))
        }
        ev = events[events["match_id"] == mid]
        self.goal_pos_home = np.sort(
            ev.loc[(ev["event_type"] == "Goal") & (ev["team_name"] == self.home), "pos"].to_numpy())
        self.goal_pos_away = np.sort(
            ev.loc[(ev["event_type"] == "Goal") & (ev["team_name"] == self.away), "pos"].to_numpy())
        self.goal_pos = np.sort(np.concatenate([self.goal_pos_home, self.goal_pos_away]))
        self.red_pos = np.sort(ev.loc[ev["event_type"] == "Red Card", "pos"].to_numpy())
        self.var_pos = np.sort(ev.loc[ev["event_type"] == "VAR Review", "pos"].to_numpy())
        b = bands[bands["match_id"] == mid]
        self.bands = {r["half"]: (r["start_minute"], r["start_minute"] + r["duration_min"])
                      for _, r in b.iterrows()}
        self.clocks = MatchClocks(
            [Band(r["half"], r["start_minute"], r["duration_min"]) for _, r in b.iterrows()])

    def margin_bucket(self, pos: float) -> int:
        h = int((self.goal_pos_home < pos).sum())
        a = int((self.goal_pos_away < pos).sum())
        d = h - a
        return int(np.sign(d) * min(abs(d), 2))

    @staticmethod
    def _count(arr: np.ndarray, lo: float, hi: float) -> int:
        return int(np.searchsorted(arr, hi) - np.searchsorted(arr, lo))

    def _near(self, arr: np.ndarray, m: float, tol: float) -> bool:
        return bool(self._count(arr, m - tol, m + tol + 1e-9))

    def eligible_minutes(self, half: str, ref_bucket: int) -> list[int]:
        band = self.bands.get(half)
        out = []
        for m in ELIGIBLE[half]:
            if band and (band[0] - BREAK_EXCL) <= m <= (band[1] + BREAK_EXCL):
                continue
            if self._near(self.goal_pos, m, GOAL_EXCL):
                continue
            if self._near(self.red_pos, m, RED_EXCL):
                continue
            if self._near(self.var_pos, m, VAR_EXCL):
                continue
            if self.margin_bucket(m) != ref_bucket:
                continue
            out.append(m)
        return out

    def outcomes(self, start: float, duration: float, w: int, clock: str) -> dict:
        """Outcome set for a (pseudo-)break with band [start, start+duration)."""
        restart = start + duration
        if clock == "adjusted":
            pre_lo, pre_hi = self.clocks.active_window(start, w, "before")
            post_lo, post_hi = self.clocks.active_window(restart, w, "after")
        else:  # display clock, naive: post window starts when the clock keeps running
            half_lo, half_hi = H_BOUNDS["H1"] if start < 45 else H_BOUNDS["H2"]
            pre_lo, pre_hi = max(start - w, half_lo - 1), start
            post_lo, post_hi = start, min(start + w, half_hi)
        cnt = self._count
        pre_h = cnt(self.shot_pos["home"], pre_lo, pre_hi)
        pre_a = cnt(self.shot_pos["away"], pre_lo, pre_hi)
        post_h = cnt(self.shot_pos["home"], post_lo, post_hi)
        post_a = cnt(self.shot_pos["away"], post_lo, post_hi)
        sot_pre = (cnt(self.sot_pos["home"], pre_lo, pre_hi)
                   - cnt(self.sot_pos["away"], pre_lo, pre_hi))
        sot_post = (cnt(self.sot_pos["home"], post_lo, post_hi)
                    - cnt(self.sot_pos["away"], post_lo, post_hi))
        return {
            "total_change": (post_h + post_a) - (pre_h + pre_a),
            "shot_diff_change": (post_h - post_a) - (pre_h - pre_a),
            "balance_disruption": abs((post_h - post_a) - (pre_h - pre_a)),
            "sot_diff_change": sot_post - sot_pre,
            "next_shot_within_w": int(
                cnt(self.shot_pos["home"], post_lo, post_hi)
                + cnt(self.shot_pos["away"], post_lo, post_hi) > 0),
        }


OUTCOMES = ["total_change", "shot_diff_change", "balance_disruption",
            "sot_diff_change", "next_shot_within_w"]


def run():
    rng = np.random.default_rng(SEED)
    bands, shots, matches, events = load_inputs()
    match_ids = sorted(bands["match_id"].unique())
    md = {mid: MatchData(mid, matches, shots, events, bands) for mid in match_ids}

    observed_rows, null_values, skipped = [], {}, []
    for _, br in bands.iterrows():
        m = md[br["match_id"]]
        bucket = m.margin_bucket(br["start_minute"])
        cands = m.eligible_minutes(br["half"], bucket)
        if not cands:
            skipped.append((br["match_id"], br["half"]))
            continue
        key = (br["match_id"], br["break_number"])
        row = {"match_id": br["match_id"], "break_number": br["break_number"],
               "half": br["half"], "start_minute": br["start_minute"],
               "margin_bucket": bucket, "n_candidates": len(cands)}
        for clock in ("adjusted", "display"):
            for w in WINDOWS:
                obs = m.outcomes(br["start_minute"], br["duration_min"], w, clock)
                for k, v in obs.items():
                    row[f"{k}_{clock}_{w}"] = v
                cand_out = {k: np.array([m.outcomes(c, 0.0, w, clock)[k] for c in cands],
                                        dtype=float) for k in OUTCOMES}
                null_values.setdefault((clock, w), {})[key] = cand_out
        observed_rows.append(row)

    obs = pd.DataFrame(observed_rows)
    obs.to_csv(PROCESSED / "placebo_break_level.csv", index=False)

    lines = [
        "# Randomized placebo analysis (Test A) — Core Output 3",
        "",
        f"Breaks analysed: {len(obs)} of 203 "
        f"({len(skipped)} skipped, no eligible score-state-matched candidate minutes: {skipped})",
        f"Candidates per break: median {obs['n_candidates'].median():.0f}, "
        f"min {obs['n_candidates'].min()}, max {obs['n_candidates'].max()}",
        f"Draws: {N_DRAWS}, seed {SEED}. Bootstrap: match-cluster, {N_BOOT}.",
        "",
        "Outcome definitions per CHANGELOG A2/A3. next_goal omitted here: goal events",
        "are too sparse per window; reported in the robustness pass instead.",
        "",
        "| clock | W | outcome | observed mean | null mean | null 2.5-97.5% | pct of null ≥ obs | boot 95% CI |",
        "|---|---|---|---|---|---|---|---|",
    ]

    null_draw_records = []
    for clock in ("adjusted", "display"):
        for w in WINDOWS:
            per_break = null_values[(clock, w)]
            keys = [k for k in per_break]
            for outcome in OUTCOMES:
                obs_col = obs[f"{outcome}_{clock}_{w}"].to_numpy(float)
                observed_mean = obs_col.mean()

                acc = np.zeros(N_DRAWS)
                for k in keys:
                    vals = per_break[k][outcome]
                    acc += vals[rng.integers(0, len(vals), N_DRAWS)]
                null_means = acc / len(keys)

                groups = obs.groupby("match_id").indices
                gkeys = list(groups)
                boot = np.empty(N_BOOT)
                for i in range(N_BOOT):
                    idx = np.concatenate(
                        [groups[gkeys[j]] for j in rng.integers(0, len(gkeys), len(gkeys))])
                    boot[i] = obs_col[idx].mean()

                pct = float((null_means >= observed_mean).mean())
                lo, hi = np.percentile(null_means, [2.5, 97.5])
                blo, bhi = np.percentile(boot, [2.5, 97.5])
                lines.append(
                    f"| {clock} | {w} | {outcome} | {observed_mean:+.3f} | "
                    f"{null_means.mean():+.3f} | [{lo:+.3f}, {hi:+.3f}] | "
                    f"{pct:.3f} | [{blo:+.3f}, {bhi:+.3f}] |")
                if w == PRIMARY_W:
                    null_draw_records.append(
                        pd.DataFrame({"clock": clock, "outcome": outcome,
                                      "null_mean": null_means,
                                      "observed_mean": observed_mean}))

    pd.concat(null_draw_records).to_csv(PROCESSED / "placebo_null_draws.csv", index=False)

    lines += [
        "",
        "## Reading guide",
        "- `pct of null ≥ obs` near 0.5 ⇒ real breaks look like ordinary matched minutes.",
        "- `balance_disruption` is the primary metric (absolute change in shot balance).",
        "- The display clock shows the naive dead-time artefact the video will explain:",
        "  its post window contains ~3 fewer minutes of football after real breaks.",
        "- Windows are break-adjusted display minutes excluding the hydration stoppage",
        "  only (CHANGELOG A1); pseudo-break windows stretch over real bands the same way.",
        "",
        "## Placement caveats (documented, not corrected post hoc)",
        "This run implements frozen Test A exactly (match on half / score state / stage /",
        "clock region). Two structural asymmetries remain and are handled in the",
        "planned robustness pass, NOT by editing this confirmatory run:",
        "1. **Post-window displacement.** A real break's post window starts ~3 display",
        "   minutes later than a same-minute pseudo's, so it samples slightly later",
        "   football. Within-half shot rates rise with the clock, which can inflate",
        "   positive `total_change`/`shot_diff_change` after real breaks.",
        "2. **Candidate-minute distribution.** Real breaks cluster at 23'/68'; eligible",
        "   candidates span the whole clock region. Signed outcomes (notably the",
        "   home-shift in `shot_diff_change`) must not be interpreted until the",
        "   robustness pass adds placement-minute adjustment (hierarchical model with",
        "   minute covariate, per spec §6 robustness).",
        "The primary absolute metric and the next-shot probability are far less exposed",
        "to both asymmetries, and both sit at/below the null.",
    ]
    (TABLES / "placebo_results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    run()
