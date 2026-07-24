import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PROCESSED = ROOT / "data" / "processed"


@pytest.fixture(scope="session")
def matches() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "matches.csv")


@pytest.fixture(scope="session")
def breaks() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "breaks.csv")


@pytest.fixture(scope="session")
def venues() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "venues.csv")


@pytest.fixture(scope="session")
def exclusions() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "exclusions.csv")


@pytest.fixture(scope="session")
def coverage() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "source_coverage.csv")
