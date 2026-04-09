# HVAC / Home Services Direct Mail Targeting

Build a tightened direct mail target list for HVAC and home services companies. Finds aging, owner-occupied homes with long-tenure owners most likely to have outdated HVAC systems and be receptive to outreach.

![HVAC Direct Mail Demo](../../assets/gifs/hvac_small.gif)

## What You Get

An interactive HTML map and CSV direct mail list with:

- All qualifying homes as clickable map dots, color-coded by owner type (original owner vs second owner)
- Original owner flagging — homes that have never changed hands have the highest probability of aging HVAC systems
- Density-based cluster detection showing the best neighborhoods to canvass
- Clickable zone diagnostics explaining why each zone was prioritized (skill mode)
- Route-optimized delivery zones with 80/20 prioritization and tabbed lead list (skill mode)
- CSV export with `original_owner` column, sorted in walk order for efficient flyer drops

## Choose Your Path

### Basic (Copy & Paste)

Copy the prompt from [`basic/PROMPT.md`](basic/PROMPT.md) into Claude Code. Targets Houston by default. Change the market name for any metro.

### Advanced (Skill)

Run `/hvac-direct-mail [market name]` for the full pipeline with density-grid route optimization, 80/20 zone prioritization, and nearest-neighbor walk sequencing.

See the [skill definition](../../.claude/skills/hvac-direct-mail/SKILL.md) for full details.

## Target Criteria

| Filter | Value | Signal |
|---|---|---|
| Property type | Single-family | Primary HVAC customer base |
| Age | 10+ years old | Systems approaching or past useful life |
| Owner-occupied | Yes | Decision-maker lives on-site |
| Not listed for sale | Yes | Not moving, receptive to investment |
| Lifetime sales | 2 or fewer | Long-tenure owners with original or aging systems |
| Original owner | 1 lifetime sale | Highest priority — HVAC system has never been replaced by a previous buyer |

## Why It Works

The average residential HVAC system lasts 15-20 years. Homes 10+ years old with long-tenure owners are statistically the most likely to need replacement or major service. Filtering to owner-occupied, not-for-sale properties ensures you reach homeowners who will actually invest in their property.
