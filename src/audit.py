"""Source inventory: hashes, sizes, row/column counts, missingness.

Output: data/processed/source_inventory.csv
Also checks the hydration repo's README claims against actual files and writes
reports/tables/audit_claims.md.

Run:  python -m src.audit
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

from .util import ANALYTICS, EXTERNAL, FIFA, HYD, PROCESSED, TABLES, load_json

RETRIEVED_AT = "2026-07-24"

# Files that feed the analysis. wc26-analytics contributes code, not data, so
# only its parser modules are inventoried (for provenance of Milestone 2).
INVENTORY = {
    "wc2026-hydration-momentum": [
        "data/treated_covariates.json",
        "data/control_candidates_all.json",
        "data/break_times_exact.json",
        "data/manifest.json",
        "data/_gv.json",
    ],
    "FIFA-World-Cup-2026-Dataset": [
        "matches.csv",
        "matches_detailed.csv",
        "venues.csv",
        "match_events.csv",
        "match_lineups.csv",
        "match_team_stats.csv",
        "player_stats.csv",
        "teams.csv",
        "referees.csv",
        "tournament_stages.csv",
    ],
    "wc26-analytics": [
        "wc26/fifa_pdf.py",
        "wc26/statsbomb.py",
        "wc26/fetch.py",
    ],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def commit_of(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def describe_json(path: Path):
    d = load_json(path)
    if isinstance(d, list):
        rows = len(d)
        if rows and isinstance(d[0], dict):
            keys = set()
            for r in d:
                keys.update(r)
            cols = len(keys)
            missing_cells = sum(len(keys) - len(r) for r in d)
            miss = missing_cells / (rows * cols) if rows * cols else 0.0
        else:
            cols, miss = 1, 0.0
        return rows, cols, round(miss, 4)
    if isinstance(d, dict):
        return len(d), None, None
    return None, None, None


def describe_csv(path: Path):
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    miss = float(df.isna().to_numpy().mean()) if df.size else 0.0
    return len(df), df.shape[1], round(miss, 4)


def build_inventory() -> pd.DataFrame:
    rows = []
    for repo_name, files in INVENTORY.items():
        repo = EXTERNAL / repo_name
        commit = commit_of(repo)
        for rel in files:
            p = repo / rel
            if not p.exists():
                rows.append(
                    dict(source_name=repo_name, repository=repo_name, commit_hash=commit,
                         relative_path=rel, sha256=None, bytes=None, rows=None,
                         columns=None, missingness=None, retrieved_at=RETRIEVED_AT,
                         notes="FILE MISSING"))
                continue
            if p.suffix == ".json":
                r, c, m = describe_json(p)
            elif p.suffix == ".csv":
                r, c, m = describe_csv(p)
            else:
                r, c, m = None, None, None
            rows.append(
                dict(source_name=repo_name, repository=repo_name, commit_hash=commit,
                     relative_path=rel, sha256=sha256(p), bytes=p.stat().st_size,
                     rows=r, columns=c, missingness=m, retrieved_at=RETRIEVED_AT,
                     notes=""))
    return pd.DataFrame(rows)


def check_readme_claims() -> list[str]:
    """Compare handoff/README claims with what the files actually contain."""
    lines = ["# Audit: README/handoff claims vs shipped files", ""]
    treated = load_json(HYD / "data" / "treated_covariates.json")
    controls = load_json(HYD / "data" / "control_candidates_all.json")
    manifest = load_json(HYD / "data" / "manifest.json")
    exact = load_json(HYD / "data" / "break_times_exact.json")

    matches = {r["match_id"] for r in treated}
    comps = {r["comp"] for r in controls}

    def claim(text, ok):
        lines.append(f"- {'CONFIRMED' if ok else '**REFUTED**'}: {text}")

    claim(f"203 treated break events (actual: {len(treated)})", len(treated) == 203)
    claim(f"102 treated matches (actual: {len(matches)})", len(matches) == 102)
    claim(f"8,946 control minutes (actual: {len(controls)})", len(controls) == 8946)
    claim(f"11 control competitions (actual: {len(comps)}: {sorted(comps)})", len(comps) == 11)
    claim(f"break_times_exact covers 32 knockout matches (actual: {len(exact)})", len(exact) == 32)

    standalone = ["wc2026_group_momentum.json", "wc2026_knockout_raw.json", "xg_2026.json"]
    shipped = [f for f in standalone if (HYD / "data" / f).exists()]
    claim(
        "README-advertised standalone SofaScore arrays are NOT shipped "
        f"(missing: {[f for f in standalone if f not in shipped]}); "
        "manifest.json carries fixture/goal/break summaries keyed by those names "
        f"(keys: {sorted(k for k in manifest if not k.startswith('__'))})",
        not shipped,
    )

    fi = [g for g in manifest["wc2026_group_momentum.json"] if g["id"] == 15186769]
    fi_breaks = fi[0]["breaks"] if fi else None
    claim(
        "France-Iraq (15186769) has no second-half break in shipped data "
        f"(manifest breaks: {fi_breaks}; treated halves: "
        f"{sorted(r['half'] for r in treated if r['match_id'] == 15186769)}). "
        "Internal sources agree; still requires INDEPENDENT external verification "
        "before it enters the report.",
        fi_breaks is not None and len(fi_breaks) == 1,
    )

    events = pd.read_csv(FIFA / "match_events.csv", encoding="utf-8-sig")
    n_subs = (events["event_type"].str.lower().str.contains("sub")).sum()
    claim(
        f"FIFA-dataset match_events.csv has {len(events)} rows, zero substitutions "
        f"(actual sub rows: {n_subs}; event types: {sorted(events['event_type'].unique())})",
        n_subs == 0,
    )
    return lines


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    inv = build_inventory()
    inv.to_csv(PROCESSED / "source_inventory.csv", index=False,
               quoting=csv.QUOTE_MINIMAL)
    print(f"source_inventory.csv: {len(inv)} files inventoried")
    print(inv[["relative_path", "rows", "columns", "missingness"]].to_string(index=False))

    lines = check_readme_claims()
    (TABLES / "audit_claims.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
