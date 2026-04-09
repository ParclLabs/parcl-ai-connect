# Pool Service — New Homeowner Targeting

Identify new homeowners who just bought a home with a pool. These buyers don't have an existing pool service relationship and are in "set up my new home" mode — the highest-conversion window for pool service companies.

![Pool Service Targeting Demo](../../assets/gifs/pools_small.gif)

## What You Get

An interactive HTML map and CSV lead list with:

- Every confirmed pool home sold in the last 4-6 weeks as a clickable map dot
- Color-coded by recency: Strike Now (red), This Month (orange), Follow-up (yellow)
- Density-based cluster detection showing the best neighborhoods to canvass
- Clickable zone diagnostics explaining why each zone was prioritized, with full property table (skill mode)
- Route-optimized delivery zones with timing tiers and tabbed lead list with click-to-pan (skill mode)
- CSV export sorted by zone tier, timing tier, and route order for efficient door-to-door outreach

## Choose Your Path

### Basic (Copy & Paste)

Copy the prompt from [`basic/PROMPT.md`](basic/PROMPT.md) into Claude Code. Targets Phoenix by default. Change the market name for any Sun Belt metro.

### Advanced (Skill)

Run `/pool-service-targeting [market name]` for the full pipeline with timing tiers ("Strike Now" / "This Month" / "Follow-up"), density-grid route optimization, and 80/20 zone prioritization.

See the [skill definition](../../.claude/skills/pool-service-targeting/SKILL.md) for full details.

## Target Criteria

| Filter | Value | Signal |
|---|---|---|
| Property type | Single-family | Primary pool-owning segment |
| Has pool | Yes (confirmed) | Parcl Labs `has_pool` flag — not a proxy |
| Sale recency | Last 4-6 weeks | New homeowner, no existing service contract |
| Owner-occupied | Yes | Homeowner, not tenant |
| Not investor-owned | Yes | Real homeowner making service decisions |

## Why It Works

New homeowners who just bought a pool home are the single highest-conversion lead for pool service companies:

1. **No existing relationship** — previous owner's pool company doesn't transfer
2. **Unknown pool condition** — buyer may not know maintenance history, equipment age, or chemical balance
3. **Setup mindset** — they're actively signing up for utilities, landscaping, pest control — pool service fits naturally
4. **Seasonal urgency** — in Sun Belt markets, pre-summer is the critical window

## Best Markets

Pool penetration varies dramatically by metro. High-value markets for this use case:

| Metro | Pool Prevalence | Peak Season |
|---|---|---|
| Phoenix | Very high | Mar-Oct |
| Las Vegas | Very high | Apr-Sep |
| Tampa / Orlando | High | Year-round |
| Houston / Dallas | High | Apr-Oct |
| Atlanta | Moderate | May-Sep |
