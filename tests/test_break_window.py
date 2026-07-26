"""Regression tests for the exploratory clock-artefact analysis (CHANGELOG E1).

The positional-indexing defect that mapped control pools to breaks by a modulo
expression was correct only by accident (it relied on len(pools) == len(df)).
These tests pin the behaviour that made it unsafe.
"""
import numpy as np
import pandas as pd
import pytest

from src import break_window as bw


@pytest.fixture(scope="module")
def built():
    bands, cache, per_min = bw.build()
    return bands, cache, per_min


@pytest.fixture(scope="module")
def support(built):
    return bw.common_support(built[0], built[1])


def test_common_support_requires_window_validity_AND_a_real_control(built, support):
    """The 7 breaks with no eligible control must be excluded, not given a
    fabricated zero-valued one. This is why the sample is 196, matching the
    preregistered placebo, rather than 203."""
    bands, cache, _ = built
    assert len(support) == 196
    for _, b in bands.iterrows():
        lo, hi = bw.HALF[b["half"]]
        key = (int(b["match_id"]), int(b["break_number"]))
        m = cache[int(b["match_id"])]
        has_ctrl = bool(m.eligible_minutes(b["half"], m.margin_bucket(b["start_minute"])))
        window_ok = (b["start_minute"] - max(bw.WINDOWS) >= lo - 1
                     and b["start_minute"] + b["duration_min"] + max(bw.WINDOWS) <= hi)
        assert (key in support) == (window_ok and has_ctrl)


def test_results_reproducible_with_frozen_seed(built, support):
    a = bw.analyse(*built, support)
    b = bw.analyse(*built, support)
    for ra, rb in zip(a, b):
        for k in ("N", "C", "D", "D_lo", "D_hi", "A", "A_lo", "A_hi", "synth"):
            assert ra[k] == pytest.approx(rb[k]), k


def test_break_row_order_does_not_change_results(built, support):
    """The old modulo indexing silently depended on row order."""
    bands, cache, per_min = built
    base = bw.analyse(bands, cache, per_min, support)
    shuffled = bands.sample(frac=1.0, random_state=7).reset_index(drop=True)
    other = bw.analyse(shuffled, cache, per_min, support)
    for ra, rb in zip(base, other):
        # point estimates are order-invariant; bootstrap draws may differ slightly
        for k in ("N", "C", "synth", "pre"):
            assert ra[k] == pytest.approx(rb[k], abs=1e-9), k


def test_each_break_keeps_its_own_duration(built, support):
    """Synthetic dead time must use the break's own duration, never a constant."""
    bands = built[0]
    rows = bw.analyse(*built, support)
    df = rows[0]["_df"]
    merged = bands.merge(df, on=["match_id", "break_number"], suffixes=("", "_r"))
    assert (merged["duration_min"] == merged["dur"]).all()
    assert merged["dur"].nunique() > 1, "durations must not collapse to a constant"


def test_dead_share_uses_min_of_duration_and_window(built, support):
    rows = bw.analyse(*built, support)
    for r in rows:
        df = r["_df"]
        expected = np.minimum(df["dur"], r["w"]) / r["w"]
        assert np.allclose(df["dead_share"], expected)


def test_real_and_synthetic_share_the_same_sample(built, support):
    """A = real - synthetic is only meaningful on identical break sets."""
    rows = bw.analyse(*built, support)
    for r in rows:
        assert r["n_breaks"] == len(r["_df"])
        # A must equal the difference of the two reported means
        assert r["A"] == pytest.approx(r["N"] - r["synth"], abs=1e-9)


def test_measured_only_subset_is_smaller_and_all_measured(built, support):
    """Derive the expectation from the data: hardcoding it hid a real change
    when common support started requiring an eligible control."""
    bands = built[0]
    expected = sum(
        1 for _, b in bands.iterrows()
        if (int(b["match_id"]), int(b["break_number"])) in support
        and b["duration_source"] == "manifest_ok")
    rows = bw.analyse(*built, support, measured_only=True)
    for r in rows:
        assert r["n_breaks"] == expected
        assert r["n_breaks"] < len(support)
        assert r["_df"]["measured"].all()


def test_rate_gap_removes_only_leading_dead_minutes(built):
    """Synthetic stoppage inserts dead clock; it must not touch the pre-window."""
    _, _, per_min = built
    mid = next(iter(per_min))[0]
    # a window with dead=0 is just the plain rate
    for w in (3, 5):
        lo = 20
        assert bw.rate_gap(per_min, mid, lo, w, 0) == pytest.approx(
            bw.rate(per_min, mid, lo, w))
    # with dead >= w nothing live remains
    assert bw.rate_gap(per_min, mid, 20, 3, 3) == 0.0


def test_event_study_alignment_shapes(built, support):
    es = bw.event_studies(*built, support)
    n = len(es["rel"])
    assert es["res_real_mean"].shape == (n,)
    assert es["res_ctrl_mean"].shape == (n,)
    assert es["call_real"].shape[1] == n
    assert es["n_breaks"] == len(support)
    # call-aligned: the stoppage minutes must be (near) empty by construction
    zero_idx = list(es["rel"]).index(0)
    assert es["call_real"][:, zero_idx].mean() == pytest.approx(0.0, abs=1e-9)
