---
name: acquisition-targeting
description: Identify SFR portfolios showing disposition signals as bulk acquisition targets in secondary markets
user-invocable: true
argument-hint: "[market1, market2, ...]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Portfolio Acquisition Targeting

Identifies SFR portfolios likely candidates for bulk acquisition based on disposition signals in target markets.

**Target markets:** $ARGUMENTS (e.g., "Louisville, Columbus, Memphis, Birmingham")

---

## Target Portfolio Criteria

| Criterion | Threshold |
|-----------|-----------|
| Portfolio size | 20-300 doors |
| Holding period | Average 10+ years (120+ months) |
| Disposition activity | Net Seller over trailing 12 months |
| Active inventory | 3+ properties currently listed for sale |

---

## Pipeline Steps

### Step 1: Resolve Markets

Use `search_locations` to get metro-level `parcl_id` values for each target market.

### Step 2: Progressive Portfolio Search

Use `portfolio_search` with a progressive relaxation strategy:

1. **First pass:** Apply all four filters simultaneously. If zero results (common in smaller metros), relax progressively.
2. **Second pass:** Drop `on_market_flag` and `activity_type_12_mo`, keeping only portfolio size (20-300) and holding period (120+ months). Download and filter locally for net sellers and on-market status.
3. **Third pass:** Drop `min_holding_period_months`, keeping only portfolio size (20-300) and `on_market_flag: true`. Download and filter locally for holding period and activity type.

Merge both result sets for the broadest candidate universe.

### Step 3: Enrich Each Portfolio

**For-sale property details** (`investor_for_sale_properties`):
- Current listing price, days on market, number of price cuts, unrealized P&L
- Full address, listing agent name / brokerage / email / phone

**Full property list** (`investor_properties`):
- All properties ever transacted to compute buy box (beds, baths, sqft, year built, acquisition price range/median)
- Market concentration (which MSAs, how many, top market percentage)

### Step 4: Score & Rank

Score each portfolio by criteria match (X/4). When no portfolio satisfies all four criteria (common in smaller metros), rank by best-fit and explain the market dynamics driving the gap.

The absence of a perfect match is itself a useful signal. It may indicate long-hold net sellers have already cleared inventory, or that current listers are predominantly accumulating rather than exiting.

### Step 5: Build Dashboard

**HTML dashboard** (single-file, no external dependencies):

Each portfolio as a card showing:
- Portfolio name, investor ID, entity type
- Currently owned count, total transaction count, average holding period in years
- 12-month activity classification with color-coded badge
- Criteria match score (X/4) with badges for each criterion met
- Buy box summary: bed/bath range, sqft range, vintage range, median acquisition price
- Market concentration: number of MSAs, concentrated vs. spread, top market with percentage
- Table of all current for-sale listings with price, DOM, price cuts, unrealized P&L, address, agent name, brokerage, contact info

Sort portfolios by criteria match score descending, then holding period descending.

**CSV export:**
One row per for-sale listing with portfolio metadata repeated on each row (portfolio name, investor ID, size, hold period, activity, buy box, concentration) plus full listing and agent details. Include rows for net sellers with no current listings marked as "No current listings."

---

## Display Names

Never display raw `parcl_id` values in user-facing output. Always resolve to human-readable names:
- ZIP parcl_ids to actual ZIP codes and town names (e.g., `5452730` to "East Hampton (11937)")
- MSA parcl_ids to metro area names (e.g., `2900417` to "Tampa-St. Petersburg-Clearwater, FL")
- Investor IDs to standardized names from `search_investors`

Note: some MCP endpoints return IDs as floats with `.0` suffix (e.g., `5452730.0`). Strip the `.0` before any lookup or display.

---

## Data Sources

| Endpoint | Purpose |
|----------|---------|
| `search_locations` | Resolve market names to parcl_ids |
| `portfolio_search` | Find portfolios by market, size, and disposition criteria |
| `investor_for_sale_properties` | Current for-sale listings with pricing, agent details |
| `investor_properties` | Full property data for buy box computation |
