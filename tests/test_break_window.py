"""Regression tests for the exploratory clock-artefact analysis (CHANGELOG E1).

The positional-indexing defect that mapped control pools to breaks by a modulo
expression was correct only by accident (it relied on len(pools) == len(df)).
These tests pin the behaviour that made it unsafe.
"""
import numpy as np
import pandas as pd
import pytest

from src import break_window as bw
from src.util import FIFA

# These tests need the tournament metadata (match_events.csv, teams.csv), which
# lives in external/ and is deliberately NOT committed (see LICENSE). CI fetches
# it; anywhere it is absent the module skips instead of erroring.
pytestmark = pytest.mark.skipif(
    not (FIFA / "match_events.csv").exists(),
    reason="requires external/FIFA-World-Cup-2026-Dataset (not redistributed; "
           "run scripts/fetch_external.sh or see config/sources.yaml)",
)


@pytest.fixture(scope="module")
def built():
    bands, cache, per_min = bw.build()
    return bands, cache, per_min


@pytest.fixture(scope="module")
def support(built):
    return bw.common_support(built[0], built[1])


def test_no_control_window_overlaps_a_real_break(built):
    """The contamination guard. Anchor-only exclusion let 47% of controls at the
    primary window contain the actual hydration break, biasing every contrast
    toward the null. Controls must have their WHOLE span clear of the band."""
    bands, cache, _ = built
    for w in bw.WINDOWS:
        for _, b in bands.iterrows():
            m = cache[int(b["match_id"])]
            bs = b["start_minute"]
            be = bs + b["duration_min"]
            for c in m.eligible_minutes(b["half"], m.margin_bucket(bs), window=w):
                assert not (c - w < be and c + w > bs), (
                    f"control window [{c - w},{c + w}) overlaps break [{bs},{be})")


def test_common_support_requires_window_validity_AND_a_real_control(built, support):
    """Breaks with no eligible control must be EXCLUDED, never handed a
    fabricated zero-valued one. The expectation is derived from the same rule
    rather than hardcoded: the contamination fix legitimately changed the count,
    and a hardcoded number would have masked that instead of surfacing it."""
    bands, cache, _ = built
    wmax = max(bw.WINDOWS)
    expected = set()
    for _, b in bands.iterrows():
        lo, hi = bw.HALF[b["half"]]
        m = cache[int(b["match_id"])]
        window_ok = (b["start_minute"] - wmax >= lo - 1
                     and b["start_minute"] + b["duration_min"] + wmax <= hi)
        has_ctrl = bool(m.eligible_minutes(
            b["half"], m.margin_bucket(b["start_minute"]), window=wmax))
        if window_ok and has_ctrl:
            expected.add((int(b["match_id"]), int(b["break_number"])))
    assert support == expected
    assert 0 < len(support) <= len(bands)


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
