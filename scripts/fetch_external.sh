#!/usr/bin/env bash
# Fetch the external inputs this project reads but does NOT redistribute.
#
# Provenance (URLs, commit hashes, caveats) is recorded in config/sources.yaml;
# per-file SHA-256 hashes in data/processed/source_inventory.csv. Nothing here
# is committed to this repository — see the scope note in LICENSE.
#
# Usage:  bash scripts/fetch_external.sh [--metadata-only]
#
#   --metadata-only   fetch just the tournament metadata CSVs needed to run the
#                     full test suite (this is what CI does). Fast, no large
#                     downloads.
#
# Without the flag it also clones the hydration-break dataset and the StatsBomb
# historical events needed to regenerate the analysis end to end.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXT="$ROOT/external"
mkdir -p "$EXT"

FIFA_DIR="$EXT/FIFA-World-Cup-2026-Dataset"
FIFA_URL="https://github.com/mominullptr/FIFA-World-Cup-2026-Dataset.git"

fetch_metadata() {
  if [ -f "$FIFA_DIR/match_events.csv" ]; then
    echo "metadata already present -> $FIFA_DIR"
    return
  fi
  echo "fetching tournament metadata (sparse, depth 1)…"
  mkdir -p "$FIFA_DIR"
  cd "$FIFA_DIR"
  git init -q
  git remote add origin "$FIFA_URL" 2>/dev/null || true
  git config core.sparseCheckout true
  cat > .git/info/sparse-checkout <<'EOF'
matches.csv
match_events.csv
match_lineups.csv
teams.csv
venues.csv
tournament_stages.csv
squads_and_players.csv
EOF
  git pull -q --depth 1 origin main || git pull -q --depth 1 origin master
  echo "  -> $(ls *.csv | wc -l) CSVs"
}

fetch_full() {
  if [ ! -d "$EXT/wc2026-hydration-momentum/.git" ]; then
    echo "cloning hydration-break dataset…"
    git clone -q --depth 1 \
      https://github.com/Ddey07/wc2026-hydration-momentum.git \
      "$EXT/wc2026-hydration-momentum"
  fi
  if [ ! -d "$EXT/statsbomb-open-data/.git" ]; then
    echo "cloning StatsBomb open data (blobless; WC2018 + WC2022 only)…"
    git clone -q --filter=blob:none --no-checkout \
      https://github.com/statsbomb/open-data.git "$EXT/statsbomb-open-data"
    cd "$EXT/statsbomb-open-data"
    git sparse-checkout init --no-cone
    git sparse-checkout set '/data/matches/43/*'
    git checkout -q
    echo "  note: event files are pulled on demand by src/statsbomb_extract.py"
  fi
}

fetch_metadata
if [ "${1:-}" != "--metadata-only" ]; then
  fetch_full
fi

echo
echo "done. FIFA post-match PDFs are fetched separately by:"
echo "    python -m src.fetch_fifa_pdfs"
