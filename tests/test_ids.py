"""Match-identifier consistency across master tables."""


def test_match_ids_unique_and_complete(matches):
    assert len(matches) == 104
    assert matches["match_id"].is_unique
    assert set(matches["match_id"]) == set(range(1, 105))


def test_sofascore_mapping_one_to_one(matches):
    mapped = matches["sofascore_id"].dropna()
    assert mapped.is_unique
    assert len(mapped) == 103  # Jordan-Algeria absent from hydration repo


def test_break_match_ids_exist_in_matches(matches, breaks):
    assert set(breaks["match_id"]) <= set(matches["match_id"])
    assert set(breaks["sofascore_id"]) <= set(matches["sofascore_id"].dropna())


def test_venue_ids_consistent(matches, venues):
    assert venues["venue_id"].is_unique
    assert len(venues) == 16
    assert set(matches["venue_id"]) <= set(venues["venue_id"])


def test_coverage_covers_every_match(matches, coverage):
    assert set(coverage["match_id"]) == set(matches["match_id"])
