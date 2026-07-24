"""Cross-table consistency and exclusion accounting."""


def test_no_duplicate_rows(matches, breaks, venues, exclusions, coverage):
    for df in (matches, breaks, venues, exclusions, coverage):
        assert not df.duplicated().any()


def test_treated_flags_match_break_counts(matches, breaks):
    per_match = breaks.groupby("match_id").size()
    treated = matches[matches["in_treated"]]
    assert len(treated) == 102
    for _, row in treated.iterrows():
        assert per_match.get(row["match_id"], 0) == row["n_treated_breaks"]
    untreated = matches[~matches["in_treated"]]
    assert untreated["n_treated_breaks"].eq(0).all()


def test_exclusions_account_for_all_gaps(matches, breaks, exclusions):
    # 104 matches - 2 excluded = 102 treated; 102*2 breaks - 1 excluded half = 203
    excl_matches = exclusions[exclusions["entity"] == "match"]
    excl_halves = exclusions[exclusions["entity"] == "half"]
    assert len(excl_matches) == 104 - matches["in_treated"].sum()
    assert len(breaks) == 102 * 2 - len(excl_halves)
    # every excluded match id exists in matches.csv and is not treated
    m = matches.set_index("match_id")
    for mid in excl_matches["match_id"]:
        assert not m.loc[mid, "in_treated"]


def test_geo_complete(matches):
    assert matches["latitude"].notna().all()
    assert matches["longitude"].notna().all()
    assert matches["elevation_meters"].notna().all()
