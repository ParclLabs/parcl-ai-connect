---
name: broker-analytics
description: Rank brokers and agents by motivated seller distress signals, with configurable price segment and market
user-invocable: true
argument-hint: "[market name] [optional: min price, e.g. 500k, 2M, or 'all']"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Broker Analytics: Motivated Seller Analysis by Broker/Agent

Generates a 5-sheet Excel workbook analyzing agent and brokerage performance in a target market, ranked by motivated seller distress signals.

**Target market:** First argument (e.g., "Hamptons", "Houston", "Tampa")

**Price segment:** Second argument controls the minimum listing price filter:
- `2M` or `2m` (default if omitted): luxury segment, properties over $2,000,000
- `500k` or `500K`: mid-market, properties over $500,000
- `1M` or `1m`: upper market, properties over $1,000,000
- `5M` or `5m`: ultra-luxury, properties over $5,000,000
- `all` or `0`: no price filter, analyze the entire market

Parse the second argument by stripping the letter suffix and converting: `k`/`K` = multiply by 1,000, `m`/`M` = multiply by 1,000,000. If no second argument is provided, default to $2,000,000.

**Examples:**
```
/broker-analytics Hamptons           # Hamptons luxury (>$2M)
/broker-analytics Houston 500k       # Houston mid-market (>$500K)
/broker-analytics Tampa all          # Tampa full market (no filter)
/broker-analytics "Beverly Hills" 5M # Beverly Hills ultra-luxury (>$5M)
```

**Audience:** Real estate teams prospecting for listing opportunities by identifying underperforming agents and brokerages with distressed inventory.

---

## Display Names

Never display raw `parcl_id` values in user-facing output. Always resolve to human-readable names:
- ZIP parcl_ids to actual ZIP codes and town names (e.g., `5452730` to "East Hampton (11937)")
- MSA parcl_ids to metro area names (e.g., `2900417` to "Tampa-St. Petersburg-Clearwater, FL")
- Investor IDs to standardized names from `search_investors`

Note: some MCP endpoints return IDs as floats with `.0` suffix (e.g., `5452730.0`). Strip the `.0` before any lookup or display.

---

## Required Tools

| Step | Tool | Purpose |
|------|------|---------|
| Resolve market | `search_locations` | Convert market name to `parcl_id`(s). Get all relevant ZIP codes and cities. |
| Pull listings | `motivated_seller_properties` | All active for-sale listings with agent info, price, DOM, motivated seller scores. |

---

## Execution Steps

### 1. Resolve Geography

Use `search_locations` to resolve the market name into `parcl_id`(s). Think broadly. Most markets span multiple ZIP codes and town names. Run multiple searches to capture all relevant areas. Focus on ZIP-level IDs.

### 2. Pull All Listings

Call `motivated_seller_properties` with:

- `parcl_ids`: all resolved market IDs
- `sort_by`: `"latest_listing_price"`
- `sort_order`: `"desc"`
- `limit`: `50000`

Always run `preview=True` first to check credit cost, then `preview=False` to download.

### 3. Download & Filter

Retrieve the CSV via the presigned `download_url`. Filter to properties where `latest_listing_price` exceeds the parsed price threshold. If the user specified `all`, skip filtering and use all listings.

### 4. Generate Workbook

Use the bundled script:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/build_workbook.py <input_csv> <output_xlsx> --market "Market Name"
```

If the script isn't available, follow the workbook structure below using `openpyxl`.

---

## Workbook Structure: 5 Sheets

### Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Title bar background | Dark navy | `#1F4E79` |
| Title text | White bold Arial 14 | `#FFFFFF` |
| Subtitle text | Gray Arial 10 | `#666666` |
| Warning subtitle text | Dark red bold Arial 10 | `#C00000` |
| Properties header row | Medium blue | `#2E75B6` |
| Brokerage header row | Orange | `#ED7D31` |
| Agent/Distress header row | Dark red | `#C00000` |
| Fire sale row highlight | Light red | `#FFC7CE` |
| Motivated row highlight | Light yellow | `#FFEB9C` |
| Above-market-avg row highlight | Cream | `#FFF2CC` |
| "vs Market Avg" negative delta cell | Red text on red bg | text `#9C0006`, bg `#FFC7CE` |
| "vs Market Avg" positive delta cell | Green text on green bg | text `#006100`, bg `#C6EFCE` |

### Formatting Standards

- Font: Arial 10pt throughout, Arial 14pt bold for titles
- Number formats: Currency `$#,##0`, Percent `0.0%`, Score `0.00`, DOM `0`, vs-Market `+0.00;-0.00;0.00`
- All data sheets: freeze panes below header, auto-filter on header row
- Title row: merged across all columns, dark navy background
- Row-level color coding on Sheet 2 based on `motivated_seller_index_label`:
  - `fire_sale` → entire row gets `#FFC7CE`
  - `motivated` → entire row gets `#FFEB9C`
  - `stubborn` / `neutral` → no highlight

---

### Sheet 1: Executive Summary

A dashboard with market-level KPIs. Layout (A=labels, B=values):

**Row 1** (merged A1:H1): `{MARKET} FOR-SALE MARKET: MOTIVATED SELLER ANALYSIS BY BROKER/AGENT`, dark navy bg, white bold 14pt

**Row 2** (merged A2:H2): `Properties Listed Over {PRICE_THRESHOLD} | Data as of {date} | Source: Parcl Labs`, gray 10pt

**Row 4** (merged A4:C4): `MARKET SNAPSHOT`, bold, light blue bg (`#D6E4F0`), navy text (`#1F4E79`)

| Row | A (bold label) | B (value) |
|-----|----------------|-----------|
| 5 | Total Listings | count |
| 6 | Listings with Agent Data | count where agent_name is not null |
| 7 | Unique Brokerages | nunique of agent_business |
| 8 | Unique Agents | nunique of agent_name |
| 9 | Median Listing Price | median of latest_listing_price (fmt: `$#,##0`) |
| 10 | Avg Days on Market | mean of days_on_market (fmt: `0`) |
| 11 | Avg Motivated Seller Score | mean of motivated_seller_index_value (fmt: `0.00`) |
| 12 | Fire Sale Properties | count where label == fire_sale |
| 13 | Motivated Properties | count where label == motivated |
| 14 | Stubborn Properties | count where label == stubborn |
| 15 | Neutral Properties | count where label == neutral |

**Row 17** (merged A17:E17): `MOTIVATED SELLER LABEL DISTRIBUTION`, bold, light blue bg, navy text

| Row | A (bold) | B | C | D | E |
|-----|----------|---|---|---|---|
| 18 | Label | Count | % of Total | Avg Price | Avg DOM |
| 19-22 | fire_sale / motivated / stubborn / neutral | computed values | | | |

**Row 24** (merged A24:H24): `KEY INSIGHT`, bold, light blue bg, navy text

**Rows 25-26** (merged A25:H26): Narrative insight paragraph:
`Market avg motivated seller score is {avg_score:.2f}. Brokerages/agents scoring ABOVE this average have listings that are sitting longer, cutting prices more, and signaling more seller distress, a potential indicator of overpricing or underperformance relative to the market.`

Column widths: A=32, B=22, C=16, D-H=13

---

### Sheet 2: All Properties Over {PRICE_THRESHOLD}

All listings above the price threshold sorted by `motivated_seller_index_value` descending (most distressed first), then by `days_on_market` descending.

**Row 1** (merged): `ALL {MARKET} PROPERTIES FOR SALE OVER {PRICE_THRESHOLD}`, dark navy bg, white 14pt bold

**Row 2** (header row): medium blue bg (`#2E75B6`), white bold Arial 10pt

| Column | Header | Source Field | Format |
|--------|--------|-------------|--------|
| A | Parcl Property ID | `parcl_property_id` | |
| B | Address | `address1` | |
| C | City | `city` | |
| D | ZIP | `zip5` | |
| E | Type | `property_type` | |
| F | Beds | `bedrooms` | |
| G | Baths | `bathrooms` | |
| H | Sq Ft | `sq_ft` | |
| I | Year Built | `year_built` | |
| J | Current Price | `latest_listing_price` | `$#,##0` |
| K | Initial Price | `initial_listing_price` | `$#,##0` |
| L | Days on Market | `days_on_market` | |
| M | Price Cuts | `num_price_cuts` | |
| N | % Price Change | `percent_change_listing_price` | `0.0%` |
| O | Motivated Score | `motivated_seller_index_value` | `0.00` |
| P | Motivated Label | `motivated_seller_index_label` | |
| Q | Agent Name | `agent_name` | |
| R | Brokerage | `agent_business` | |
| S | Agent Email | `agent_email` | |
| T | Agent Phone | `agent_phone` | |
| U | Owner Entity | `entity_name` | |
| V | Original Purchase Price | `original_purchase_price` | `$#,##0` |
| W | Unrealized P&L | `unrealized_net` | `$#,##0` |

Row coloring: `#FFC7CE` for `fire_sale`, `#FFEB9C` for `motivated`, no fill for others.

Freeze pane: `A3`. Auto-filter on row 2.

---

### Sheet 3: Brokerage Analysis

Aggregated by `agent_business`, ranked by avg motivated seller score descending (worst performers at top).

**Row 1** (merged): `BROKERAGE PERFORMANCE: RANKED BY MOTIVATED SELLER SCORE (UNDERPERFORMERS AT TOP)`, dark navy bg, white 14pt bold

**Row 2** (merged): `Market Avg Motivated Score: {avg:.2f} | Brokerages above this line are underperforming the market`, dark red bold 10pt (`#C00000`)

**Row 3** (header): Orange bg (`#ED7D31`), white bold Arial 10pt

| Column | Header | Calculation |
|--------|--------|------------|
| A | Brokerage | Group key (bold in data rows) |
| B | # Listings | Count |
| C | Avg Motivated Score | Mean motivated_seller_index_value (fmt: `0.00`) |
| D | vs Market Avg | score - market_avg (fmt: `+0.00;-0.00;0.00`) |
| E | Avg Days on Market | Mean DOM (fmt: `0`) |
| F | Avg Price Cuts | Mean num_price_cuts (fmt: `0.0`) |
| G | Avg % Price Change | Mean percent_change_listing_price (fmt: `0.0%`) |
| H | Total Listing Value | Sum latest_listing_price (fmt: `$#,##0`) |
| I | Avg Listing Price | Mean latest_listing_price (fmt: `$#,##0`) |
| J | Fire Sale | Count where label == fire_sale |
| K | Motivated | Count where label == motivated |
| L | Neutral + Stubborn | Count where label in (neutral, stubborn) |

Row highlighting: rows where avg score > market avg get cream bg (`#FFF2CC`). The "vs Market Avg" cell: positive values get red text (`#9C0006`) on red bg (`#FFC7CE`); negative/zero get green text (`#006100`) on green bg (`#C6EFCE`).

Freeze pane: `A4`. Auto-filter on row 3.

---

### Sheet 4: Agent Analysis

Aggregated by `agent_name` + `agent_business`, ranked by avg motivated seller score descending.

**Row 1** (merged): `AGENT PERFORMANCE: RANKED BY MOTIVATED SELLER SCORE (UNDERPERFORMERS AT TOP)`, dark navy bg, white 14pt bold

**Row 2** (merged): `Market Avg Motivated Score: {avg:.2f} | Agents above this line have more distressed listings`, dark red bold 10pt

**Row 3** (header): Dark red bg (`#C00000`), white bold Arial 10pt

| Column | Header | Calculation |
|--------|--------|------------|
| A | Agent | Group key (bold in data rows) |
| B | Brokerage | Group key |
| C | # Listings | Count |
| D | Avg Motivated Score | Mean score (fmt: `0.00`) |
| E | vs Market Avg | score - market_avg (fmt: `+0.00;-0.00;0.00`) |
| F | Avg Days on Market | Mean DOM (fmt: `0`) |
| G | Avg Price Cuts | Mean cuts (fmt: `0.0`) |
| H | Avg % Price Change | Mean pct change (fmt: `0.0%`) |
| I | Total Value | Sum latest_listing_price (fmt: `$#,##0`) |
| J | Fire Sales | Count fire_sale |
| K | Motivated | Count motivated |

Row highlighting: same logic as Sheet 3.

Freeze pane: `A4`. Auto-filter on row 3.

---

### Sheet 5: Fire Sale & Motivated Detail

Only properties with `motivated_seller_index_label` in (`fire_sale`, `motivated`), sorted by score descending then DOM descending.

**Row 1** (merged): `FIRE SALE & MOTIVATED PROPERTIES: {MARKET}`, dark red bg (`#C00000`), white 14pt bold

**Row 2** (header): Dark red bg (`#C00000`), white bold Arial 10pt

| Column | Header | Source | Format |
|--------|--------|--------|--------|
| A | Parcl Property ID | `parcl_property_id` | |
| B | Address | `address1` | |
| C | City | `city` | |
| D | ZIP | `zip5` | |
| E | Current Price | `latest_listing_price` | `$#,##0` |
| F | Initial Price | `initial_listing_price` | `$#,##0` |
| G | Days on Market | `days_on_market` | |
| H | Price Cuts | `num_price_cuts` | |
| I | % Price Change | `percent_change_listing_price` | `0.0%` |
| J | Motivated Score | `motivated_seller_index_value` | `0.00` |
| K | Label | `motivated_seller_index_label` | |
| L | Agent | `agent_name` | |
| M | Brokerage | `agent_business` | |
| N | Owner Entity | `entity_name` | |
| O | Unrealized P&L | `unrealized_net` | `$#,##0` |

Row coloring: `fire_sale` rows get `#FFC7CE`, `motivated` rows get no special fill (to distinguish from fire_sale).

Freeze pane: `A3`. Auto-filter on row 2.

---

## Example Usage

```
/broker-analytics Hamptons
/broker-analytics Beverly Hills
/broker-analytics Palm Beach
/broker-analytics Aspen
```
