"""Physical-layer integrity, incl. the sprints/top-speed swap correction."""
import pandas as pd
import pytest

from tests.conftest import PROCESSED


@pytest.fixture(scope="module")
def phys():
    return pd.read_csv(PROCESSED / "physical_2026.csv")


def test_sprints_are_integer_counts(phys):
    # A fractional sprint count is the signature of the PDF column swap.
    assert (phys["sprints"].dropna() % 1 == 0).all()


def test_top_speed_plausible(phys):
    ts = phys["top_speed_kmh"].dropna()
    assert ts.between(18, 40).all(), "top speeds outside 18-40 km/h imply a bad swap"


def test_swap_flag_present_and_reasonable(phys):
    assert "phys_col_swap_fixed" in phys.columns
    # ~5% of rows (mostly goalkeepers) needed the fix; guard against regressions
    assert 100 <= phys["phys_col_swap_fixed"].sum() <= 200


def test_distances_plausible(phys):
    assert phys["total_distance_m"].dropna().between(0, 17000).all()
    assert (phys["zone5_m"] <= phys["total_distance_m"]).all()
