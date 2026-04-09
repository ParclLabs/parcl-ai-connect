---
name: pm-fragmentation
description: Analyze property management fragmentation across SFR portfolios to identify consolidation opportunities
user-invocable: true
argument-hint: "[market name or 'top-10']"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Property Manager Fragmentation Analysis

Identifies fragmented property management relationships across SFR portfolios, surfacing portfolio owners who may benefit from consolidated PM services.

**Target:** $ARGUMENTS. Pass a single market name for single-market analysis, or "top-10" to anchor on the top 10 markets by institutional SFR presence.

---

## Pipeline Steps

### Step 1: Identify Target Markets

**Multi-market mode ("top-10"):**
1. Use `search_investors` to find the largest institutional SFR operator's `investor_id`.
2. Pull `investor_msa_activity` and rank markets by property count. Take the top 10.

**Single-market mode:**
1. Use `search_locations` to resolve the market name to a `parcl_id`.

### Step 2: Find 50+ Unit Portfolios

Run `portfolio_search` across each target MSA filtered to a minimum of 50 units. This captures institutional and mid-size operators large enough to need professional management but small enough that they may not have it figured out.

Exclude portfolios with more than 500 units nationally. These are institutional operators who self-manage or have locked-in PM relationships.

### Step 3: Pull Rental Property Data with PM Details

Use `investor_rental_properties` for every portfolio identified. Key fields:
- `enhanced_manager_agent_business`: the PM company managing the listing
- `enhanced_manager_property_manager`: the specific property manager

### Step 4: Normalize PM Names

Raw data contains dozens of variants for the same PM company. Normalize aggressively:
- Strip LLC/Inc/Llc suffixes
- Consolidate known brand variants
- Group blank/missing entries as "Unknown/Self-Managed"

Common normalizations:
- "American Homes 4 Rent" / "Amh (American Homes 4 Rent)" / "Amh.Com" → American Homes 4 Rent
- "Firstkey Homes" / "Firstkey Homes, Llc" / "Firstkey Homes Llc" → FirstKey Homes
- "Darwin Homes" / "Darwin Homes, Llc." / "Darwin Properties" → Darwin Homes
- "Mynd" / "Mynd Property Management" / "Mynd Management" → Mynd
- "Tricon Residential" / "Tricon" / "Tah [State] Llc" → Tricon Residential

### Step 5: Score PM Concentration

For each portfolio in each market, calculate the share of known-PM-managed units per property manager. Classify:

| Classification | Criteria |
|---|---|
| Single PM | One PM manages everything |
| Concentrated | Top PM holds 85%+ share |
| Moderately Concentrated | Top PM holds 60-84% |
| Fragmented | Top PM holds 40-59% |
| Highly Fragmented | Top PM holds less than 40% |
| Self-Managed/Unknown | No identifiable PM |

**Opportunity scoring:**
- **High**: Fragmented or Highly Fragmented with 50+ rental units
- **Medium**: Same classification with 20-49 units, or Self-Managed/Unknown with 50+ units
- **Low-Medium**: Moderately Concentrated with 3+ PMs and 50+ units

### Step 6: Build Dashboard

Produce a single interactive HTML file (dark theme, all text bright white) with:

**Multi-market mode:**
- KPI bar: portfolios analyzed, portfolio-market combos, high-opportunity count, medium-opportunity count
- Market cards (2 rows x 5): MSA name, total institutional units, portfolio count, opportunity badges, stacked classification bar. Clickable for drill-down.
- Opportunity targets table: filterable by signal level. Columns: Market, Owner, Rental Units, # of PMs, PM Mix (inline colored segments with hover tooltips), Top PM, Top PM Share, 2nd PM, 2nd PM Share, Classification, Opportunity Signal.
- Market drill-down: appears on card click, showing every portfolio ranked by opportunity then size.

**Single-market mode:**
- KPI bar: portfolios analyzed, total rental units covered, high-opportunity count, medium-opportunity count
- Portfolio summary: ranked by opportunity signal then size, with classification badges
- Opportunity targets table: same columns as multi-market
- Portfolio drill-down: clickable rows expanding to full PM breakdown per portfolio

No Unknown % column. It adds noise without changing the signal.

---

## Reference

See `examples/tampa-single-market.md` for a complete single-market specification applied to Tampa.

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
| `search_investors` | Find anchor investor for market selection |
| `investor_msa_activity` | Market-level property counts for ranking |
| `search_locations` | Resolve market names to parcl_ids |
| `portfolio_search` | Find portfolios by market and size criteria |
| `investor_rental_properties` | Property-level rental data with PM company details |
