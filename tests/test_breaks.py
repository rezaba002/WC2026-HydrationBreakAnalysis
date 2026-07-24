"""Break-level validity: uniqueness, halves, timing order, ranges."""


def test_expected_break_counts(breaks):
    assert len(breaks) == 203
    assert (breaks["half"] == "H1").sum() == 102
    assert (breaks["half"] == "H2").sum() == 101


def test_break_uniqueness(breaks):
    assert not breaks.duplicated(subset=["match_id", "break_number"]).any()
    assert not breaks.duplicated(subset=["sofascore_id", "break_number"]).any()
    assert breaks["unit"].is_unique


def test_valid_half_values(breaks):
    assert set(breaks["half"]) == {"H1", "H2"}
    assert set(breaks["break_number"]) == {1, 2}
    h1 = breaks[breaks["half"] == "H1"]
    h2 = breaks[breaks["half"] == "H2"]
    assert (h1["break_number"] == 1).all()
    assert (h2["break_number"] == 2).all()


def test_break_minutes_in_plausible_windows(breaks):
    h1 = breaks[breaks["half"] == "H1"]["start_minute"]
    h2 = breaks[breaks["half"] == "H2"]["start_minute"]
    assert h1.between(20, 35).all()
    assert h2.between(60, 80).all()


def test_timing_order_and_duration(breaks):
    ok = breaks[breaks["band_quality"] == "ok"]
    assert (ok["manifest_end"] > ok["manifest_start"]).all()
    assert ok["duration_display_min"].between(1, 6).all()
    # flagged bands never carry a duration
    flagged = breaks[breaks["band_quality"] == "implausible_end"]
    assert flagged["duration_display_min"].isna().all()
    # the corrupt-end defect is a known source issue in ~14 group bands;
    # fail loudly if a rebuild changes its footprint
    assert len(flagged) <= 20


def test_timing_sources_agree(breaks):
    checked = breaks.dropna(subset=["timing_consistent"])
    assert checked["timing_consistent"].all()


def test_wbgt_plausible(breaks):
    assert breaks["wbgt"].between(5, 45).all()
