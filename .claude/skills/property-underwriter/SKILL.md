---
name: property-underwriter
description: Generate a lender-grade underwriting report for any US residential address — imputed current value from the Parcl Labs price index, 3-mile sale and rental comps, gross yield, and risk notes in a polished HTML dashboard
user-invocable: true
argument-hint: "[address]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Property Underwriter

Generate a comprehensive lender underwriting report for a US residential property using Parcl Labs data. The report includes an imputed current value, comparable sales, comparable rental listings, gross yield, and risk commentary — all rendered in a polished dark-themed HTML dashboard.

**Subject property:** $ARGUMENTS (e.g., "1097 Greenbriar Rd, Bethel Park, PA 15102")

## Prerequisites

This skill requires the **Parcl Labs MCP**. Before starting, confirm the connection is available by checking for tools matching `search_properties`, `search_locations`, `property_events`, and `sale_price_index`.

## Workflow

### Step 1 — Identify the Subject Property

Use `search_properties` with the full address. The search is relevance-ranked text matching — it returns the closest candidates, not guaranteed exact matches, which makes it resilient to typos but means the match must be verified before underwriting.

**Verify the match.** Normalize both the input address and each returned `addr_str` (uppercase, strip punctuation) and compare on **street number, street name, and ZIP**:

- **Exact match** → proceed. State the matched address so the user sees what is being underwritten.
- **No exact match, but close candidates** (likely typo — transposed digits, misspelled street, wrong suffix like Rd/Dr/St): pick the best guess, but **stop and confirm with the user before proceeding**. Show the candidate's full address plus its beds/baths/sqft/year so they can recognize the property, e.g. "I couldn't find '1097 Greenbrier Dr' but found **1097 GREENBRIAR RD, BETHEL PARK, PA 15102** (3 BD / 1 BA, 1,032 sqft, built 1960) — is this the property you intended?" If several candidates are plausible, list them and let the user choose.
- **No close candidates in the right area**: retry with relaxed queries before giving up — street number + street name + ZIP is the most reliable (e.g. "1097 Greenbrier 15102" recovers the property despite a misspelled street and missing suffix), then number + street + city. A candidate whose **state or ZIP doesn't match the input is not a candidate** — relevance search can return a confident-looking property in a different state (e.g. "Greenbrier" matching a Tennessee town name instead of the street); discard those rather than offering them as best guesses.
- **No plausible candidates** → report that the address was not found and ask for a corrected address.

**Never underwrite an unconfirmed substitute.** Do not silently proceed with a near-match, do not use neighboring addresses as a stand-in, and do not impute a value from nearby sales. The user must explicitly confirm any property that isn't an exact match — an underwriting report against the wrong collateral is worse than no report.

From the confirmed match, record:

- `parcl_property_id`, `latitude`, `longitude`
- `property_type` (SINGLE_FAMILY, CONDO, TOWNHOUSE, OTHER)
- beds, baths, sqft, year_built

### Step 2 — Find the Market Location

Use `search_locations` with the property's ZIP code and `location_type: "zip"` to get the `parcl_id`. Record `has_sales_data` and `has_rentals_data` for later.

### Step 3 — Pull Subject Transaction History

Use `property_events` with the subject's `parcl_property_id`, `include_property_details: true`, and `include_full_event_history: true`. Download the CSV and identify:

- **Last sale price and date** (most recent SOLD event)
- **Prior sale price and date** (if available, useful for showing historical appreciation)

**If the property has no SOLD event in its history, STOP.** The imputed-value methodology requires a real transaction on the subject property as its baseline. Report that the property was found but has no recorded sale, and do not substitute a reference price from other properties.

### Step 4 — Download the Sale Price Index

The price index is essential for imputing the current value. It provides a daily $/sqft time series for a geographic area. Try to get it at the most granular level available using this cascade:

1. **ZIP code** (`parcl_id` from Step 2)
2. **County** (search with `location_type: "county"`)
3. **Metro / MSA** (search with `location_type: "metro"`)
4. **Broader metro** (search for the broader CBSA — e.g., "Greenville-Anderson" if "Spartanburg" returns nothing)

At each level, call `sale_price_index` and check `record_count`. If 0, move to the next level. Record which geography you used — this is a transparency disclosure in the report.

Download the CSV when you get a hit. Extract:

- The index value closest to the **last sale date** (or reference date)
- The **most recent** index value
- Monthly samples for the price trend chart

### Step 5 — Impute Current Value

```text
imputed_value = last_sale_price × (current_index / index_at_sale_date)
pct_change = (current_index - index_at_sale_date) / index_at_sale_date × 100
```

If the sale date predates the index start (the index typically begins Dec 2019), use the earliest available index value and note this gap in the methodology section — it means actual appreciation from the sale may differ from what the index captures.

### Step 6 — Pull Comparable Sales

Use `property_events` with:

- `geo_coordinates`: subject lat/lon with `radius: 3` (miles)
- `property_types`: match the subject's type (e.g., `["SINGLE_FAMILY"]`)
- `event_names`: `["SOLD"]`
- `start_date` / `end_date`: trailing 6 months from today
- `include_property_details: true`

First do a `preview: true` call to check estimated records and credits. Then download with `preview: false`.

**Data cleaning**: Filter out bulk/portfolio transfers. These show up as prices well above market (often $1M+ for properties that should be ~$300k) and are institutional lot purchases, not arm's-length transactions. A reasonable filter is to exclude prices above a sensible ceiling for the market — typically 3-4× the median. Review the data and apply judgment.

Compute:

- Median and mean sale price
- Median and mean $/sqft
- Price range (min/max)
- Price distribution buckets (for histogram chart)

### Step 7 — Pull Comparable Rentals

Same geo/property_type filters as Step 6, but with `event_names: ["LISTED_RENT"]`.

Compute:

- Median and mean monthly rent
- Rent range

### Step 8 — Compute Risk Metrics

```text
annual_rent = median_monthly_rent × 12
gross_yield = annual_rent / imputed_value × 100
rent_to_value = median_monthly_rent / imputed_value × 100
```

Also compare the subject's implied $/sqft (imputed_value / sqft) against the comp median $/sqft — this tells the lender whether the subject is priced above or below the local market.

### Step 9 — Generate the HTML Report

Run the bundled report generator script:

```bash
python3 .claude/skills/property-underwriter/scripts/generate_report.py \
  --data report_data.json \
  --output underwriting_report_<slug>.html
```

The `report_data.json` file should contain all the computed data from Steps 1-8 in this structure:

```json
{
  "subject": {
    "address", "city", "state", "zip", "county", "metro",
    "beds", "baths", "sqft", "year_built", "property_type",
    "lat", "lon", "owner_occupied", "investor_owned", "on_market",
    "last_sale_price", "last_sale_date",
    "prior_sale_price", "prior_sale_date"
  },
  "price_index": {
    "pi_at_sale_date", "pi_sale_date_used", "pi_current", "pi_current_date",
    "pct_change", "imputed_value", "index_name" (geography used),
    "monthly_chart_data": [{"date": "YYYY-MM-DD", "value": float}, ...]
  },
  "comp_sales": {
    "count", "median_price", "mean_price", "min_price", "max_price",
    "median_ppsf", "mean_ppsf", "median_sqft",
    "top_comps": [{"address", "city", "zip", "beds", "baths", "sqft",
                    "year_built", "price", "date", "ppsf"}, ...],
    "price_buckets": [["$100k-$150k", 12], ...]
  },
  "comp_rentals": {
    "count", "median_rent", "mean_rent", "min_rent", "max_rent",
    "top_comps": [{"address", "city", "zip", "beds", "baths", "sqft",
                    "year_built", "rent", "date"}, ...]
  },
  "metrics": {
    "gross_yield", "annual_rent", "monthly_rent_to_value"
  }
}
```

If the script is unavailable for any reason, construct the HTML inline following the design pattern described below.

### Report Design Specification

The report uses a dark professional theme suitable for financial/lending contexts:

- **Color palette**: Navy background (#0f1a2e), surface cards (#1e2d45), blue accent (#3b82f6), cyan (#06b6d4), green (#10b981), amber (#f59e0b), red (#ef4444)
- **Layout**: Full-width header with address + badges, then a max-width 1280px container
- **KPI row**: 4 cards across the top — Imputed Value, Last Sale Price, Est. Market Rent, Price Index
- **Subject & Valuation**: Two-column grid — property details on left, valuation math on right
- **Charts** (Chart.js 4.x): Price index trend line + comp sale price distribution histogram
- **Comp tables**: Sortable-looking tables with summary stats bar above each
- **Methodology & Risk Notes**: Prose section explaining the valuation approach, data sources, and key risk factors

### Step 10 — Verify and Deliver

Before delivering:

1. Verify the imputed value math programmatically (price × ratio = expected)
2. Verify the gross yield math
3. Confirm comp counts match the data

Save the report to the working directory and provide the file path.

## Risk Factors to Assess

The methodology section should address these risk dimensions (where applicable):

- **Property age and condition** — older homes (pre-1970) with limited bathrooms or small footprints may have functional obsolescence
- **Size relative to comps** — if the subject is materially smaller or larger than the comp median, note the divergence
- **Price index baseline gap** — if the sale predates the index start, the imputed value has a wider confidence interval
- **New construction premium** — new builds trade at a $/sqft premium that compresses as the home ages
- **Institutional investor activity** — if AMH, Invitation Homes, or other institutions are active in the area, note concentration risk
- **Market trend direction** — if the price index shows recent softening, flag near-term downside risk
- **Gross yield stress test** — suggest stress-testing the yield against vacancy, maintenance, insurance, and taxes

## Data Sources

| Endpoint | Purpose |
|----------|---------|
| `search_properties` | Resolve the subject address to a property record |
| `search_locations` | Resolve ZIP/county/metro to parcl_ids |
| `property_events` | Subject transaction history, comparable sales, comparable rentals |
| `sale_price_index` | $/sqft time series for imputing current value |
