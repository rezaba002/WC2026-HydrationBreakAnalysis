# Substitution timing — 2026 vs 2018/2022 (Core Output 4)

Regulation-time substitution events: WC2018 364, WC2022 562, WC2026 956.
All comparisons use tournament shares (3-sub era vs 5-sub era).
Association, not causation (spec §8).

## Clustering on the actual second break

Matches with a known second break and H2 subs: 100
2026 H2 subs within ±3' of the own-match break: **154/825 = 18.7%**
Minute-matched expectation from WC2018: 19.6% (excess: -0.9%, ratio 0.95x)
Minute-matched expectation from WC2022: 20.7% (excess: -2.1%, ratio 0.90x)

**Exploratory displacement pattern** (not preregistered, label as such):
- during the 3' before the stoppage: 2026 6.8% vs hist 7.6%/8.5% — deficit
- 3' from the restart: 2026 15.0% vs hist 12.6%/14.6% — surplus

## Context statistics

First substitution minute (median per team-match): WC2018 61', WC2022 57', WC2026 58'
Regulation subs per team-match: WC2018 2.87, WC2022 4.39, WC2026 4.64
Score state at substitution (share): 2026 trailing 35%; 2026 level 34%; 2026 leading 32%
  WC2018: trailing 35%; level 33%; leading 32%
  WC2022: trailing 36%; leading 34%; level 30%

## Notes
- 2026 sub minutes come from PMSR markers with lineup-derived fallback;
  stoppage-time rounding documented in HANDOFF_STATE §5.
- Matches without a known second break (44, 1) and France-Iraq H2 are
  excluded from the ±3' statistic.
- Extra-time substitutions excluded everywhere.
- The 85-90' tail is NOT comparable across sources: StatsBomb stoppage
  subs are clipped to 90 while the 2026 parser rounds them into 85-90.
  Do not interpret the late-minute excess; it is a recording artefact
  plus longer 2026 added time (quantified in Core Output 6).
