"""Discover and download FIFA Post Match Summary Report PDFs.

Source: fifatrainingcentre.com match-report hubs (public, free PDFs).
Rate-limited (3 s between requests), cached, resumable. Raw PDFs preserved in
data/raw/fifa_pdfs/ with an index of URLs and hashes.

Run:  python -m src.fetch_fifa_pdfs [--discover-only]
"""
from __future__ import annotations

import hashlib
import re
import sys
import time
import unicodedata
from pathlib import Path

import pandas as pd
import requests

from .util import PROCESSED, ROOT

RAW = ROOT / "data" / "raw" / "fifa_pdfs"
BASE = "https://www.fifatrainingcentre.com"
HUBS = [
    f"{BASE}/en/fifa-world-cup-2026/match-report-hub.php",
    f"{BASE}/en/fifa-world-cup-2026/match-report-hub-knockout-stage.php",
]
UA = {"User-Agent": "wc2026-hydration-impact research (contact: rezaba002 on GitHub)"}
SLEEP_S = 3

# FIFA-dataset team_name -> FIFA 3-letter code (48 qualified teams)
TEAM_CODE = {
    "Mexico": "MEX", "South Africa": "RSA", "South Korea": "KOR", "Czechia": "CZE",
    "Canada": "CAN", "Bosnia and Herzegovina": "BIH", "USA": "USA", "Paraguay": "PAR",
    "Haiti": "HAI", "Scotland": "SCO", "Australia": "AUS", "Türkiye": "TUR",
    "Brazil": "BRA", "Morocco": "MAR", "Qatar": "QAT", "Switzerland": "SUI",
    "Spain": "ESP", "Argentina": "ARG", "France": "FRA", "England": "ENG",
    "Germany": "GER", "Portugal": "POR", "Netherlands": "NED", "Belgium": "BEL",
    "Uruguay": "URU", "Colombia": "COL", "Ecuador": "ECU", "Senegal": "SEN",
    "Ghana": "GHA", "Côte d'Ivoire": "CIV", "Egypt": "EGY", "Tunisia": "TUN",
    "Algeria": "ALG", "Japan": "JPN", "Saudi Arabia": "KSA", "IR Iran": "IRN",
    "New Zealand": "NZL", "Panama": "PAN", "Croatia": "CRO", "Sweden": "SWE",
    "Norway": "NOR", "Austria": "AUT", "Uzbekistan": "UZB", "Iraq": "IRQ",
    "Jordan": "JOR", "Curaçao": "CUW", "Congo DR": "COD", "Cabo Verde": "CPV",
}


def discover() -> pd.DataFrame:
    """Scrape hub pages -> one row per PDF: match_num, home_code, away_code, url."""
    seen_hubs, to_visit, hrefs = set(), list(HUBS), []
    while to_visit:
        url = to_visit.pop(0)
        if url in seen_hubs:
            continue
        seen_hubs.add(url)
        time.sleep(SLEEP_S)
        resp = requests.get(url, headers=UA, timeout=30)
        resp.raise_for_status()
        hrefs += re.findall(r'href=["\']([^"\']+\.pdf)["\']', resp.text, re.I)
        for h in re.findall(r'href=["\']([^"\']*match-report-hub[^"\']*\.php)["\']',
                            resp.text, re.I):
            full = h if h.startswith("http") else BASE + h
            if full not in seen_hubs:
                to_visit.append(full)

    rows, seen_urls = [], set()
    for href in hrefs:
        stem = Path(href).stem.upper()
        stem = re.sub(r"[\s\-]*(POST|V\d+|FINAL)[\s\-]*$", "", stem.strip())
        m = re.search(r"M(\d+)[\s\-]+([A-Z]+)[\s\-]V[\s\-]([A-Z]+)", stem)
        if not m:
            continue
        url = href if href.startswith("http") else BASE + href
        if url in seen_urls:
            continue
        seen_urls.add(url)
        rows.append(
            {"match_num": int(m.group(1)), "home_code": m.group(2),
             "away_code": m.group(3), "url": url}
        )
    return pd.DataFrame(rows).sort_values("match_num").reset_index(drop=True)


def map_to_matches(index: pd.DataFrame) -> pd.DataFrame:
    """Join discovered PDFs to matches.csv by unordered team-code pair.

    FIFA's official match numbering does NOT equal the dataset's date-ordered
    match_id, but team pairs are unique across the tournament (verified in
    Milestone 1), so the code pair is a safe key. The official number is kept
    as fifa_official_match_num.
    """
    matches = pd.read_csv(PROCESSED / "matches.csv")
    matches["home_code"] = matches["home"].map(TEAM_CODE)
    matches["away_code"] = matches["away"].map(TEAM_CODE)
    assert matches["home_code"].notna().all() and matches["away_code"].notna().all(), \
        "unmapped team name in TEAM_CODE"

    by_pair = {}
    for _, r in index.iterrows():
        by_pair.setdefault(frozenset((r["home_code"], r["away_code"])), []).append(r)
    dupes = {k: v for k, v in by_pair.items() if len(v) > 1}
    assert not dupes, f"ambiguous PDF code pairs: {dupes}"

    rows = []
    for _, m in matches.iterrows():
        hit = by_pair.get(frozenset((m["home_code"], m["away_code"])))
        r = hit[0] if hit else None
        rows.append(
            {
                **m[["match_id", "home", "away", "home_code", "away_code"]].to_dict(),
                "fifa_official_match_num": None if r is None else r["match_num"],
                "home_code_pdf": None if r is None else r["home_code"],
                "away_code_pdf": None if r is None else r["away_code"],
                "url": None if r is None else r["url"],
                "orientation_flipped": None if r is None
                else r["home_code"] != m["home_code"],
            }
        )
    merged = pd.DataFrame(rows)
    merged["codes_verified"] = merged["url"].notna()
    return merged


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_all(merged: pd.DataFrame):
    RAW.mkdir(parents=True, exist_ok=True)
    rows = []
    for _, r in merged.iterrows():
        if pd.isna(r["url"]):
            rows.append({"match_id": r["match_id"], "status": "no_pdf_found"})
            continue
        dest = RAW / f"M{int(r['match_id']):03d}_{r['home_code_pdf']}-{r['away_code_pdf']}.pdf"
        if not (dest.exists() and dest.stat().st_size > 10_000):
            time.sleep(SLEEP_S)
            try:
                resp = requests.get(r["url"], headers=UA, timeout=120)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
            except Exception as exc:
                rows.append({"match_id": r["match_id"], "status": f"download_failed: {exc}"})
                print(f"M{r['match_id']}: FAILED {exc}", flush=True)
                continue
        rows.append(
            {"match_id": r["match_id"], "status": "ok", "file": dest.name,
             "bytes": dest.stat().st_size, "sha256": sha256(dest), "url": r["url"],
             "codes_verified": r["codes_verified"]}
        )
        print(f"M{r['match_id']}: {dest.name} ({dest.stat().st_size // 1024} KB)", flush=True)
    pd.DataFrame(rows).to_csv(RAW / "index.csv", index=False)


def main():
    index = discover()
    print(f"discovered {len(index)} PDFs "
          f"(match numbers {index['match_num'].min()}-{index['match_num'].max()})")
    merged = map_to_matches(index)
    n_ok = merged["codes_verified"].sum()
    print(f"mapped to matches.csv: {merged['url'].notna().sum()}/104 with URL, "
          f"{n_ok} verified by team code")
    mismatch = merged[merged["url"].notna() & ~merged["codes_verified"]]
    if len(mismatch):
        print("code mismatches:")
        print(mismatch[["match_id", "home", "away", "home_code_pdf", "away_code_pdf"]]
              .to_string(index=False))
    if "--discover-only" in sys.argv:
        return
    download_all(merged)


if __name__ == "__main__":
    main()
