"""The commercial question — inventory created, motive NOT inferred.

The loudest public claim about the breaks was that FIFA sold football's soul for
advertising money. This module handles that claim under the project's frozen
claims discipline (spec §13):

  SUPPORTED    the breaks created a large, guaranteed, predictable block of
               in-match stoppage — this module quantifies it from our own data.
  DOCUMENTED   broadcasters and trade press reported new advertising inventory
               around the breaks; FIFA publicly denied a revenue motive.
  NOT CLAIMED  that FIFA introduced the breaks in order to sell advertising.
               Nothing in any dataset we hold speaks to intent, and no amount
               of inventory arithmetic can establish motive.

What the deferral gate means: the original handoff deferred "broadcast ad-coding"
until all seven core outputs existed. They now do, so the commercial question is
in scope — but actual ad-coding needs broadcast footage we do not have and
cannot obtain. What IS available is the inventory arithmetic, which is the part
that rests on our own measurements rather than on anyone's assertion.

Outputs: reports/tables/commercial.md
Run:     python -m src.commercial
"""
from __future__ import annotations

import pandas as pd

from .util import PROCESSED, TABLES


def main():
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    matches = pd.read_csv(PROCESSED / "matches.csv")

    n_breaks = len(bands)
    total_min = float(bands["duration_min"].sum())
    median_dur = float(bands["duration_min"].median())
    n_matches = int(bands["match_id"].nunique())
    per_match = total_min / n_matches
    tournament_matches = len(matches)
    # what the policy guarantees, independent of what we recorded
    guaranteed_slots = tournament_matches * 2
    guaranteed_min = guaranteed_slots * median_dur

    lines = [
        "# The commercial question — what the breaks created",
        "",
        "The most widely repeated criticism of the policy was that FIFA interrupted",
        "football to sell advertising. This section separates what our data can",
        "establish from what it cannot.",
        "",
        "## What our data establishes: the inventory",
        "",
        "| quantity | value |",
        "|---|---|",
        f"| Breaks recorded | {n_breaks} across {n_matches} matches |",
        f"| Median break duration | {median_dur:.1f} min |",
        f"| Total recorded break time | {total_min:.0f} min ({total_min/60:.1f} hours) |",
        f"| Per match | {per_match:.1f} min |",
        f"| Guaranteed by policy, whole tournament | {guaranteed_slots} slots "
        f"across {tournament_matches} matches (~{guaranteed_min/60:.1f} hours) |",
        "",
        "Three properties matter commercially, and all three are ours to state because",
        "they follow from the policy and our own timing data:",
        "",
        "1. **Guaranteed.** Every match, both halves, irrespective of weather [1]. Unlike",
        "   injury stoppages, the inventory exists before a ball is kicked.",
        "2. **Predictable.** Breaks cluster at 23' and 68', so the slot can be sold and",
        "   scheduled in advance rather than filled reactively.",
        "3. **Inside the match.** The clock runs and the time is added back as stoppage",
        "   time [1], so the audience does not disperse the way it does at half-time.",
        "",
        "That combination — guaranteed, predictable, mid-match — is what distinguishes",
        "this from ordinary stoppage. It is a structural fact, not an accusation.",
        "",
        "## What is documented but not ours",
        "",
        "Trade and general press reported substantial new advertising inventory and",
        "revenue attached to the breaks [12]. We reproduce none of those figures as our",
        "own: we did not audit broadcaster revenue, did not code a single advertisement,",
        "and hold no contract or ratings data.",
        "",
        "## What we explicitly do NOT claim",
        "",
        "**That FIFA introduced hydration breaks in order to create advertising",
        "inventory.** No dataset in this project speaks to intent. FIFA presented the",
        "policy as player welfare [1], and its president publicly denied a financial",
        "motive, stating there was no additional revenue for FIFA and that it was not a",
        "financial issue for them (Goal.com; logged in our perception rejections as",
        "RJ-012 because it is a policy statement, not a match-level claim).",
        "",
        "Both of the following are true at once, and the honest sentence keeps them",
        "side by side:",
        "",
        "> FIFA called the breaks a player-welfare measure. The policy also created",
        "> roughly ten hours of guaranteed, predictable, mid-match commercial inventory",
        "> that had not previously existed.",
        "",
        "Motive would require evidence we do not have: internal deliberations, contract",
        "timelines, or rights-negotiation records. Anyone asserting it — in either",
        "direction — is going beyond the public data.",
        "",
        "## A note on the strongest counter-argument",
        "",
        "The welfare rationale is weakest exactly where the commercial one is strongest:",
        f"only 38 of {n_breaks} breaks (19%) occurred at or above the WBGT threshold that",
        "made cooling breaks mandatory under FIFA's own previous protocol (report §2).",
        "Four in five breaks happened in conditions the old rules did not consider to",
        "require one. That does not demonstrate a commercial motive either — a union",
        "would argue the old threshold was simply too high, and FIFPRO has argued exactly",
        "that [4]. But it is the fact that makes the question legitimate rather than",
        "cynical, and it belongs in the record.",
    ]
    (TABLES / "commercial.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
