# Perception-Claim Codebook

**Preregistered:** 2026-07-24, before any claim collection began.
**Status:** FROZEN. The inclusion rule and coding fields below may not change after
collection starts. Any clarification is appended to §7 with a date, never edited in
place, and never applied retroactively to already-coded claims without a re-coding
pass of ALL claims.

The perception dataset is central to the project's originality. Its headline result:

> What proportion of specific public momentum claims were supported by an
> objectively unusual post-break change?

---

## 1. Inclusion rule (frozen)

Include a claim **only** when a commentator, manager, player, or major media outlet
explicitly attributes a change in a **specific match** to a **specific hydration
break**.

### Valid examples
- "The break stopped Team A's momentum."
- "The coach used the break to change formation."
- "Team B improved immediately after the hydration break."
- "The interruption helped the defending team regroup."

### Invalid examples
- Generic criticism of hydration breaks (no specific match)
- Unspecific claims that breaks are disruptive
- Comments with no identifiable match or break
- Retrospective claims that cannot be tied to an event
- Fan posts without sufficient source reliability (a clearly separated
  audience-perception sample may collect these later, but never in this dataset)

## 2. Source reliability tiers

| tier | definition | included? |
|---|---|---|
| A | live broadcast commentary; manager/player quotes in press conferences | yes |
| B | major-outlet match reports and analysis (national broadsheet, Opta, ESPN, BBC, beIN, etc.) | yes |
| C | aggregator blogs, minor outlets | only with a directly quoted A/B-tier speaker |
| D | anonymous fan posts, forums, social media | no |

## 3. Coding fields

Template: `data/manual/perception_claims.csv`.

| field | rule |
|---|---|
| `claim_id` | `PC-###`, sequential in collection order |
| `match_id` | FIFA-backbone match id (1–104) from `data/processed/matches.csv` |
| `break_number` | 1 or 2; if the claim covers both breaks, one row per break with a note |
| `published_at` | ISO date of the source |
| `source_type` | `commentary` / `manager` / `player` / `media` |
| `claim_text` | verbatim quotation, translated if needed, translation noted |
| `claimed_team_helped` / `claimed_team_harmed` | team name as in `matches.csv`; blank if not directional |
| `claimed_mechanism` | `momentum_stop` / `tactical_change` / `physical_recovery` / `regroup` / `other` |
| `collection_query` | the exact search query or broadcast segment that surfaced it |
| `verification_status` | `verbatim_confirmed` / `secondhand` — secondhand needs two sources |
| `objective_*` | LEFT BLANK during collection; filled in the blinded evaluation phase |
| `supports_claim` | LEFT BLANK during collection; coded per §5 |

## 4. Collection discipline

1. Search **systematically**, not only for famous reversals: iterate over ALL 104
   matches (including the 3 documented exclusions) with the same query template per
   match, in match-id order, before any free-form searching.
2. Record every rejected candidate in `perception_rejections.csv` with the reason —
   rejections are data.
3. Target ≈ 40 usable claims. Stop conditions are time-based, not result-based:
   never stop because the tally "looks right".
4. Free-form collection may not begin before this codebook was frozen (it was).

## 5. Blinded objective evaluation (after collection freezes)

1. Freeze `perception_claims.csv` (hash it into `source_inventory.csv`).
2. A separate pass computes `objective_pre_xg`, `objective_post_xg`,
   `objective_pre_shots`, `objective_post_shots`, `next_goal_team` from the
   independent event layer (Milestone 2), WITHOUT the claim text visible.
3. `supports_claim` is coded mechanically against the preregistered definition of
   "objectively unusual": the post-break change exceeds the 80th percentile of the
   randomized pseudo-break distribution for the same match state (Test A machinery).
   Direction must match the claim's direction.
4. Values: `supported` / `not_supported` / `indeterminate` (missing event data).

## 6. What this dataset can and cannot say

It measures **availability bias**: how often a publicly claimed momentum swing
corresponds to an objectively unusual swing. It does not measure whether breaks
"work", and a low support rate does not mean commentators lie — it means memorable
cases are remembered and the dozens of uneventful breaks are not.

## 7. Dated clarifications (append-only)

*(none yet)*
