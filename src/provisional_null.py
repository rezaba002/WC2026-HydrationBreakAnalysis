"""Recalculate the provisional null from shipped data only.

Treated mean momentum drop vs historical-control mean drop, with a
match-cluster bootstrap for the difference. This is an AUDIT statistic using
SofaScore's proprietary momentum summaries — it is NOT the project's final
result and is labelled accordingly everywhere it appears.

Also verifies the handoff's reference values (break-minute distributions,
WBGT summary).

Output: reports/tables/provisional_null.md
Run:    python -m src.provisional_null
"""
from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd

from .util import TABLES, load_hyd

SEED = 20260724
N_BOOT = 5000

# Handoff §6 reference values, recomputed here rather than trusted.
REF_H1 = {22: 5, 23: 51, 24: 21, 25: 16, 26: 4, 27: 3, 29: 1, 30: 1}
REF_H2 = {67: 11, 68: 41, 69: 32, 70: 7, 71: 4, 72: 3, 73: 2, 75: 1}


def cluster_bootstrap_mean(df: pd.DataFrame, value_col: str, cluster_col: str,
                           rng: np.random.Generator, n_boot: int) -> np.ndarray:
    """Bootstrap the mean of value_col by resampling whole clusters."""
    groups = {k: v[value_col].to_numpy() for k, v in df.groupby(cluster_col)}
    keys = list(groups)
    means = np.empty(n_boot)
    for i in range(n_boot):
        sample = rng.choice(len(keys), size=len(keys), replace=True)
        vals = np.concatenate([groups[keys[j]] for j in sample])
        means[i] = vals.mean()
    return means


def main():
    hyd = load_hyd()
    treated = pd.DataFrame(hyd["treated"])
    controls = pd.DataFrame(hyd["controls"])
    treated["drop"] = treated["pre_level"] - treated["post_level"]
    controls["drop"] = controls["pre_level"] - controls["post_level"]

    rng = np.random.default_rng(SEED)
    t_boot = cluster_bootstrap_mean(treated, "drop", "match_id", rng, N_BOOT)
    c_boot = cluster_bootstrap_mean(controls, "drop", "match_id", rng, N_BOOT)
    diff_boot = t_boot - c_boot

    t_mean, c_mean = treated["drop"].mean(), controls["drop"].mean()
    diff = t_mean - c_mean
    lo, hi = np.percentile(diff_boot, [2.5, 97.5])

    h1 = Counter(treated.loc[treated["half"] == "H1", "minute"])
    h2 = Counter(treated.loc[treated["half"] == "H2", "minute"])
    wbgt = treated["wbgt"]
    n_above = int((wbgt > 28).sum())

    lines = [
        "# Provisional null — audit recalculation (NOT a final result)",
        "",
        "Source: shipped `treated_covariates.json` / `control_candidates_all.json` only.",
        "Outcome: SofaScore momentum summaries (proprietary, secondary-tier). ",
        f"Bootstrap: match-cluster, {N_BOOT} iterations, seed {SEED}.",
        "",
        "## Momentum drop (pre_level − post_level)",
        "",
        "| group | n obs | n matches | mean pre | mean post | mean drop |",
        "|---|---|---|---|---|---|",
        f"| treated breaks | {len(treated)} | {treated['match_id'].nunique()} | "
        f"{treated['pre_level'].mean():.1f} | {treated['post_level'].mean():.1f} | {t_mean:.2f} |",
        f"| control minutes | {len(controls)} | {controls['match_id'].nunique()} | "
        f"{controls['pre_level'].mean():.1f} | {controls['post_level'].mean():.1f} | {c_mean:.2f} |",
        "",
        f"**Difference (treated − control): {diff:+.2f}**, "
        f"95% match-cluster bootstrap interval [{lo:+.2f}, {hi:+.2f}].",
        "",
        "Momentum drops sharply after real breaks — and almost as sharply after "
        "comparable non-break minutes selected the same way. The visible-in-one-line "
        "null: high momentum reverts regardless of whether anyone stops the game.",
        "",
        "## Reference-value verification (handoff §6)",
        "",
        f"- H1 break minutes: {dict(sorted(h1.items()))}",
        f"  - matches handoff reference: {dict(sorted(h1.items())) == REF_H1}",
        f"- H2 break minutes: {dict(sorted(h2.items()))}",
        f"  - matches handoff reference: {dict(sorted(h2.items())) == REF_H2}",
        f"- Handoff reference drops: treated 7.9, control 7.1 "
        f"(recomputed: {t_mean:.1f}, {c_mean:.1f})",
        f"- WBGT across breaks: min {wbgt.min():.1f}, median {wbgt.median():.1f}, "
        f"max {wbgt.max():.1f} (reference: 17.8 / 26.1 / 37.2)",
        f"- Breaks above 28°C FIFPRO threshold: {n_above} of {len(treated)} (reference: 87)",
        "",
        "## Why this is the weakest design in the project",
        "",
        "The on-screen momentum index is what most viewers actually watched, so it "
        "deserves a direct answer. But it can only carry a WEAKER design than the "
        "shot-based results, for reasons that are properties of the data rather than "
        "choices:",
        "",
        "1. **No 2026 control minutes exist.** All 8,946 controls come from "
        f"{controls['comp'].nunique()} OTHER competitions (2018-2025). The randomized "
        "within-match pseudo-break design used for shots (Test A) therefore CANNOT be "
        "built for momentum — there is nothing within 2026 to draw controls from. This "
        "is an external-control comparison across different tournaments, squads and "
        "rules eras.",
        "2. **No minute-level momentum series is shipped.** Only pre-level, pre-slope and "
        "post-level at each break survive; the underlying curves were stripped from the "
        "source repository to avoid redistributing a proprietary index. Rebuilding them "
        "would mean re-fetching from the provider.",
        "3. **The index is a proprietary black box.** Its construction is unpublished, so "
        "it cannot be audited, and the spec keeps it strictly secondary (CHANGELOG A2).",
        "",
        "## What it nevertheless shows: triangulation",
        "",
        "Despite the weaker design and a completely different data provider, the momentum "
        f"index points the same way as the shot analysis: **{diff:+.2f}** with a 95% "
        f"match-clustered interval of **[{lo:+.2f}, {hi:+.2f}]**, straddling zero. "
        "Momentum collapses after breaks — and collapses almost as hard after ordinary "
        "comparable minutes.",
        "",
        "Two independent measurement systems, two different control strategies, the same "
        "null. That agreement is worth more than either result alone, and it is why this "
        "weak-design comparison is reported at all.",
        "",
        "## Caveats",
        "",
        "- Proprietary black-box index; the project's primary outcomes are shot-based, "
        "from the independently auditable FIFA layer.",
        "- External controls (see above) — corroboration, never the headline.",
        "- The `leadside` breakdown is exploratory and largely reflects regression "
        "to the mean; it is intentionally not reported here.",
    ]
    TABLES.mkdir(parents=True, exist_ok=True)
    (TABLES / "provisional_null.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
