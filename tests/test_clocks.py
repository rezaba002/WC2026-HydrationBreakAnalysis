"""Dual-clock correctness: dead time removal, window stretching, no leakage."""
import pandas as pd
import pytest

from src.clocks import Band, MatchClocks, adjudicate_bands


@pytest.fixture
def clocks() -> MatchClocks:
    # breaks: 23'-26' (3 min) and 68'-71' (3 min)
    return MatchClocks([Band("H1", 23, 3), Band("H2", 68, 3)])


def test_active_equals_display_before_break(clocks):
    assert clocks.to_active(10) == 10
    assert clocks.to_active(23) == 23


def test_active_removes_dead_time_after_break(clocks):
    assert clocks.to_active(26) == 23   # break fully elapsed
    assert clocks.to_active(36) == 33
    assert clocks.to_active(24.5) == 23.0  # frozen mid-break

def test_h2_continuous_across_halftime(clocks):
    assert clocks.to_active(45) == 45
    assert clocks.to_active(67) == 67   # before H2 break
    assert clocks.to_active(71) == 68
    assert clocks.to_active(90) == 87


def test_in_break(clocks):
    assert clocks.in_break(23)
    assert clocks.in_break(25.9)
    assert not clocks.in_break(26)
    assert not clocks.in_break(67.9)
    assert clocks.in_break(70)


def test_window_after_stretches_over_break(clocks):
    # 10 active minutes after the 26' restart: no band crossed -> 26-36
    assert clocks.active_window(26, 10, "after") == (26, 36)
    # 10 active minutes after 20': crosses the 23-26 band -> ends 33+3=33... 20+10+3
    start, end = clocks.active_window(20, 10, "after")
    assert (start, end) == (20, 33)
    # verify the invariant directly: active span equals requested span
    assert clocks.to_active(end) - clocks.to_active(start) == 10


def test_window_before_stretches_over_break(clocks):
    start, end = clocks.active_window(30, 10, "before")
    assert (start, end) == (17, 30)
    assert clocks.to_active(end) - clocks.to_active(start) == 10


def test_window_clipped_at_half_boundary(clocks):
    start, end = clocks.active_window(40, 10, "after")
    assert end == 45  # cannot cross halftime


def test_naive_window_asymmetry_documented(clocks):
    """The motivating defect: 10 display minutes after the break start hold
    only ~7 active minutes; the active_window fixes exactly this."""
    naive_active = clocks.to_active(33) - clocks.to_active(23)
    assert naive_active == 7


def test_adjudicated_bands_complete():
    bands = adjudicate_bands()
    assert len(bands) == 203
    assert bands["duration_min"].notna().all()
    assert bands["duration_min"].between(1, 6).all()
    assert set(bands["duration_source"]) <= {"manifest_ok", "imputed_median"}
