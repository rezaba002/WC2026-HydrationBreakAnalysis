"""Draw the preregistered match sample for systematic perception collection.

The codebook mandates a per-match sweep of all 104 matches. A full sweep is one
search per match; this module instead draws a REPRODUCIBLE RANDOM SAMPLE,
stratified by stage, and emits an identical query template for each drawn match.

Why a random sample rather than a purposive one: the headline finding is the
DENOMINATOR (what share of breaks ever generated a public claim). Searching
"matches likely to have claims" would rebuild the very selection bias the
project measures. A random sample is unbiased and extensible — raising
SAMPLE_SIZE and re-running yields a superset, since the draw is seeded.

The sample is fixed BEFORE any searching, and the sweep log records a row for
every drawn match including those where nothing was found. Null results are
data.

Outputs: data/manual/perception_sweep_plan.csv
Run:     python -m src.perception_sample
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .util import PROCESSED, ROOT

SEED = 20260724
SAMPLE_SIZE = 24          # pre-specified; do NOT tune after seeing results
PLAN = ROOT / "data" / "manual" / "perception_sweep_plan.csv"

QUERY_TEMPLATE = 'World Cup 2026 {home} {away} hydration break momentum'


def main():
    m = pd.read_csv(PROCESSED / "matches.csv")
    rng = np.random.default_rng(SEED)

    # stratify by stage, proportional allocation, so knockout rounds are covered
    picks = []
    for stage, grp in m.groupby("stage_name", sort=True):
        n = max(1, round(SAMPLE_SIZE * len(grp) / len(m)))
        idx = rng.choice(grp.index.to_numpy(), size=min(n, len(grp)), replace=False)
        picks.extend(idx.tolist())

    # trim/extend to exactly SAMPLE_SIZE, still at random
    picks = list(dict.fromkeys(picks))
    if len(picks) > SAMPLE_SIZE:
        picks = rng.choice(picks, size=SAMPLE_SIZE, replace=False).tolist()
    elif len(picks) < SAMPLE_SIZE:
        rest = [i for i in m.index if i not in picks]
        picks += rng.choice(rest, size=SAMPLE_SIZE - len(picks), replace=False).tolist()

    sel = m.loc[sorted(picks)].copy()
    sel["query"] = sel.apply(
        lambda r: QUERY_TEMPLATE.format(home=r["home"], away=r["away"]), axis=1)
    out = sel[["match_id", "stage_name", "home", "away", "home_score", "away_score",
               "in_treated", "n_treated_breaks", "query"]]
    out.to_csv(PLAN, index=False)

    print(f"sample: {len(out)} matches (seed {SEED}), "
          f"{out['n_treated_breaks'].sum()} breaks in scope")
    print(out["stage_name"].value_counts().to_string())
    print()
    for _, r in out.iterrows():
        print(f"M{r['match_id']:>3}  {r['stage_name']:<18} {r['home']} v {r['away']}")


if __name__ == "__main__":
    main()
