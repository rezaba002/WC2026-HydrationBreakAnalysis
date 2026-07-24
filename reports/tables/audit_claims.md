# Audit: README/handoff claims vs shipped files

- CONFIRMED: 203 treated break events (actual: 203)
- CONFIRMED: 102 treated matches (actual: 102)
- CONFIRMED: 8,946 control minutes (actual: 8946)
- CONFIRMED: 11 control competitions (actual: 11: ['COPA2019', 'COPA2021', 'COPA2024', 'EURO2020', 'EURO2024', 'GOLD2019', 'GOLD2021', 'GOLD2023', 'GOLD2025', 'WC2018', 'WC2022'])
- CONFIRMED: break_times_exact covers 32 knockout matches (actual: 32)
- CONFIRMED: README-advertised standalone SofaScore arrays are NOT shipped (missing: ['wc2026_group_momentum.json', 'wc2026_knockout_raw.json', 'xg_2026.json']); manifest.json carries fixture/goal/break summaries keyed by those names (keys: ['wc2026_group_momentum.json', 'wc2026_knockout_raw.json', 'wc_control_group_momentum.json', 'wc_control_intl.json', 'wc_control_momentum.json', 'wc_control_pastwc.json'])
- CONFIRMED: France-Iraq (15186769) has no second-half break in shipped data (manifest breaks: [{'start': 23, 'end': 25}]; treated halves: ['H1']). Internal sources agree; still requires INDEPENDENT external verification before it enters the report.
- CONFIRMED: FIFA-dataset match_events.csv has 834 rows, zero substitutions (actual sub rows: 0; event types: ['Assist', 'Goal', 'Penalty Shootout Goal', 'Penalty Shootout Miss', 'Red Card', 'VAR Review', 'Yellow Card'])
