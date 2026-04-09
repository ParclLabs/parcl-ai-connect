---
name: competitor-analysis
description: Build a comprehensive portfolio teardown of any institutional SFR investor using Parcl Labs Portfolio Hunter
user-invocable: true
argument-hint: "[investor name]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Competitor Portfolio Analysis

Generates a comprehensive Excel workbook analyzing any institutional SFR investor across 8 analytical dimensions using Parcl Labs Portfolio Hunter data.

**Target investor:** $ARGUMENTS (e.g., any institutional SFR operator name)

---

## Pipeline Steps

### Step 1: Resolve Investor

Use `search_investors` to query the investor name and retrieve their `investor_id`.

### Step 2: Pull MSA-Level Activity

Use `investor_msa_activity` to get market-level portfolio breakdown. Rank markets by property count. Take the top 10 for detailed analysis.

### Step 3: Build 8-Tab Workbook

#### Tab 1: Portfolio Overview
- National summary: total properties, estimated portfolio value, number of MSAs, average holding period, 12-month net activity classification, active rental/for-sale counts
- Market breakdown table sorted by property count: market name, property count, % of portfolio, estimated value ($M), 12-month activity type
- National totals row

#### Tab 2: Rental Price Index
- Pull `rental_price_index` for top 10 markets by property count
- Monthly average $/sqft/month, pivoted wide (months as rows, markets as columns)
- Full available history (2020 through present)

#### Tab 3: Buy Box by Market
- Use `investor_properties` for full property-level data
- Per market + national rollup: total units, P10/Median/P90 for sqft, median beds/baths, P10/Median/P90 year built, P10/Median/P90 acquisition price

#### Tab 4: Acquisitions vs Sales
- Use `investment_activity` for full transaction history
- By market and year: purchase count, sale count, net activity, avg purchase price, avg sale price
- National rollup section

#### Tab 5: Availability & Disposition
- By top 10 market: total properties, active rentals count, % for rent, median asking rent, avg rental DOM, for-sale count, % for sale, median list price, avg sale DOM, avg price cuts, avg unrealized P&L
- Use `investor_rental_properties` (filter rental_status = "Active Rental") and `investor_for_sale_properties`

#### Tab 6: For-Sale Detail
- Property-level detail for all currently listed for-sale units
- Columns: market, address, city, state, ZIP, list price, DOM, price cuts, unrealized P&L

#### Tab 7: Investor vs Market Rents
- Join active rentals with `investor_properties` on `parcl_property_id` to get sq_ft
- Compute investor's median $/sqft/month per market
- Pull latest Parcl Labs Rental Price Index as market benchmark
- Show: market, active listings, median total rent, median sqft, investor $/sqft/mo, market $/sqft/mo (RPI), premium/(discount) %, avg price changes, avg DOM

#### Tab 8: Algorithmic Pricing Analysis
- Classify each active rental as "algo-priced" if:
  - (a) enhanced_manager_agent_email contains the investor's centralized leasing domain, OR
  - (b) listing has 3+ rental_num_price_changes (dynamic repricing signal)
- By market: active listings, algo-priced count & %, domain count & %, 3+ changes count & %, avg/median price changes, static (0 changes) count & %
- Price change frequency distribution table (national): bands 0, 1-2, 3-5, 6-10, 11-20, 21-50

---

## Formatting

- Professional Excel with consistent Arial font
- Color-coded headers: dark blue fill, white text
- Green font for positive signals (Net Buyer, premiums), red for negative (Net Seller, discounts, losses)
- Yellow highlight on premium/discount cells exceeding +/- 4%
- Green cell fill on algo-pricing % above 90%, yellow above 80%
- Number formats: $#,##0 for prices, #,##0 for counts, 0.0% for percentages, $#,##0.00 for $/sqft
- Freeze panes on all header rows
- National rollup rows with light blue fill and bold font

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
| `search_investors` | Resolve investor name → investor_id |
| `investor_msa_activity` | Market-level portfolio breakdown |
| `investor_properties` | Full property-level data (sqft, beds, baths, year_built, acquisition_price) |
| `investor_rental_properties` | Active and off-market rental listings with pricing and DOM |
| `investor_for_sale_properties` | Current for-sale listings with pricing and unrealized P&L |
| `investment_activity` | Purchase and sale transaction history |
| `rental_price_index` | Market-level rental price index for benchmarking |

---

## Workbook Generation

After downloading all CSVs, use the bundled script to build the formatted workbook:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_workbook.py \
    --msa-activity <msa_activity.csv> \
    --properties <properties.csv> \
    --rentals <rentals.csv> \
    --for-sale <for_sale.csv> \
    --transactions <transactions.csv> \
    --rpi <rpi.csv> \
    --output <output.xlsx> \
    --investor "Investor Name"
```

The script handles MSA ID normalization (some endpoints return float-formatted IDs like `2900174.0`), property sqft joins for $/sqft rent comparisons, and all conditional formatting.

If the script is not available, follow the 8-tab structure above using `openpyxl` directly.
