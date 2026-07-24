"""Dual-clock timeline: display clock vs break-adjusted clock.

The hydration break sits INSIDE the running display clock (~3 min of dead
time). The break-adjusted clock removes that dead time — and only that
(CHANGELOG A1): throw-ins, VAR and other stoppages remain. Windows on it hold
equal displayed-football time excluding the hydration stoppage.

Also adjudicates one break-band table (start + duration) per break:
  duration_source = manifest_ok        band shipped and plausible (1-6 min)
                  = imputed_median     band missing/corrupt -> tournament median

Outputs:  data/processed/break_bands.csv
Run:      python -m src.clocks
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .util import PROCESSED


@dataclass(frozen=True)
class Band:
    """One dead-time band on the match clock of a given half."""
    half: str            # "H1" | "H2"
    start: float         # display minute the break starts
    duration: float      # minutes of dead time

    @property
    def end(self) -> float:
        return self.start + self.duration


class MatchClocks:
    """Convert between display minutes and active-play minutes for one match.

    Display minutes are per-half football minutes as recorded in event feeds
    (H2 starts at 45 regardless of first-half stoppage). Bands must belong to
    the half they occur in.
    """

    def __init__(self, bands: list[Band]):
        self.bands = {"H1": [b for b in bands if b.half == "H1"],
                      "H2": [b for b in bands if b.half == "H2"]}
        for half_bands in self.bands.values():
            half_bands.sort(key=lambda b: b.start)

    @staticmethod
    def _half_of(display_minute: float) -> str:
        return "H1" if display_minute < 45 else "H2"

    def dead_time_before(self, display_minute: float) -> float:
        """Dead minutes elapsed before display_minute within its half."""
        half = self._half_of(display_minute)
        dead = 0.0
        for b in self.bands[half]:
            overlap = min(display_minute, b.end) - b.start
            if overlap > 0:
                dead += min(overlap, b.duration)
        return dead

    def to_active(self, display_minute: float) -> float:
        """Active-play minutes elapsed in the half at display_minute.

        H1 returns minutes since kickoff; H2 returns 45 + active minutes since
        restart, so the active clock is continuous across halftime.
        """
        half = self._half_of(display_minute)
        base = 0.0 if half == "H1" else 45.0
        return base + (display_minute - base) - self.dead_time_before(display_minute)

    def in_break(self, display_minute: float) -> bool:
        half = self._half_of(display_minute)
        return any(b.start <= display_minute < b.end for b in self.bands[half])

    def active_window(self, from_display: float, active_minutes: float,
                      direction: str) -> tuple[float, float]:
        """Display-minute interval containing exactly `active_minutes` of play.

        direction="after": window starts at from_display and extends forward,
        stretching over any dead time. direction="before": ends at from_display
        and extends backward. Windows are clipped at half boundaries (0/45/90 —
        added time beyond the nominal half length is not modelled at minute
        granularity).
        """
        half = self._half_of(from_display)
        lo, hi = (0.0, 45.0) if half == "H1" else (45.0, 90.0)
        if direction == "after":
            end = from_display + active_minutes
            for b in self.bands[half]:
                if b.start < end and b.end > from_display:
                    overlap = min(end, b.end) - max(from_display, b.start)
                    end += overlap  # stretch over dead time
            return from_display, min(end, hi)
        if direction == "before":
            start = from_display - active_minutes
            for b in reversed(self.bands[half]):
                if b.end > start and b.start < from_display:
                    overlap = min(from_display, b.end) - max(start, b.start)
                    start -= overlap
            return max(start, lo), from_display
        raise ValueError(direction)


def adjudicate_bands() -> pd.DataFrame:
    """One final (start, duration, source) per break from breaks.csv."""
    breaks = pd.read_csv(PROCESSED / "breaks.csv")
    median_dur = breaks.loc[breaks["band_quality"] == "ok",
                            "duration_display_min"].median()
    rows = []
    for _, r in breaks.iterrows():
        ok = r["band_quality"] == "ok"
        rows.append(
            {
                "match_id": r["match_id"],
                "sofascore_id": r["sofascore_id"],
                "break_number": r["break_number"],
                "half": r["half"],
                "start_minute": r["start_minute"],
                "duration_min": r["duration_display_min"] if ok else median_dur,
                "duration_source": "manifest_ok" if ok else "imputed_median",
            }
        )
    return pd.DataFrame(rows)


def clocks_for_match(bands_df: pd.DataFrame, match_id: int) -> MatchClocks:
    sub = bands_df[bands_df["match_id"] == match_id]
    return MatchClocks(
        [Band(r["half"], r["start_minute"], r["duration_min"]) for _, r in sub.iterrows()]
    )


def main():
    bands = adjudicate_bands()
    bands.to_csv(PROCESSED / "break_bands.csv", index=False)
    n_imputed = (bands["duration_source"] == "imputed_median").sum()
    print(f"break_bands.csv: {len(bands)} bands, {n_imputed} imputed durations, "
          f"median duration {bands['duration_min'].median()} min")

    # smoke check: the France-Sweden R32 match, first break at 23'
    example = clocks_for_match(bands, int(bands.iloc[0]["match_id"]))
    print("example match bands:", example.bands)


if __name__ == "__main__":
    main()
