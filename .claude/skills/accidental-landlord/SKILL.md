---
name: accidental-landlord
description: Build an accidental landlord lead gen pipeline that identifies failed sellers who pivoted to renting as PM prospects
user-invocable: true
argument-hint: "[market name]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Accidental Landlord Lead Generation

Generates an end-to-end lead generation pipeline identifying accidental landlords (homeowners who failed to sell and pivoted to renting) and packages them into a client-ready HTML dashboard for property management firms.

**Target market:** $ARGUMENTS (defaults to Houston MSA if not specified)

---

## Background

Parcl Labs coined "accidental landlord" to describe homeowners who enter the SFR market by necessity, not design. When a home seller can't find a buyer, they can delist and wait, cut to market clearing price, or convert to rental. The third option creates an accidental landlord, the highest-intent prospect for property management firms.

These owners didn't choose to be landlords. They have no PM experience, no tenant screening process, no maintenance network, and they need help immediately.

For full context on the research, media coverage, and methodology origins, see:
- [Media & Origin Context](reference/media-and-origin-context.md)
- [Published Research](reference/published-research.md)
- [Houston Session Methodology](reference/session-methodology.md): exact MCP tool calls that produced 1,464 leads

---

## Pipeline Steps

### Phase 1: Market Setup

1. Use `search_locations` to get the `parcl_id` for the target MSA.
2. Confirm the market has both sales and rental data.

### Phase 2: Data Pulls

Pull two datasets from `property_events`:

**For-sale listing events (lookback window):**
- `event_names`: ["LISTED_SALE", "LISTING_PRICE_CHANGE", "RELISTED"]
- `start_date`: 4-5 months before today
- `end_date`: ~45 days before today
- `property_types`: ["SINGLE_FAMILY"]
- `include_property_details`: true
- `limit`: 20000

**Rental listing events (lookahead window):**
- `event_names`: ["LISTED_RENT", "RENTAL_PRICE_CHANGE"]
- `start_date`: ~45 days before today
- `end_date`: today
- `property_types`: ["SINGLE_FAMILY"]
- `include_property_details`: true
- `limit`: 20000

**Enrichment pulls:**
- `motivated_seller_properties`: top 500 by motivated_seller_index_value. Join to AL leads on `parcl_property_id`.
- `motivated_renter_properties`: top 500 by motivated_renter_index_value. Join to AL leads on `parcl_property_id`.

### Phase 3: 110-Day Rolling Window Methodology

For each analysis date (sample every 15 days across the available range):

1. **Define windows:** Lookback = analysis_date minus 50 days → analysis_date. Lookahead = analysis_date → analysis_date plus 60 days.
2. **Find transitions:** Properties with for-sale events in lookback AND rental events in lookahead.
3. **Same-owner filter:** Compare `event_entity_owner_name` across sale and rental events. Keep only matches (including both-null as a match).
4. **Deduplicate:** Keep the earliest transition per `parcl_property_id`.
5. **Outlier filtering:**
   - Remove rents < $500/mo or > $10,000/mo
   - Remove sale prices < $50,000
   - Compute gross yield = (rental_price x 12) / sale_price x 100
   - Remove yields < 2% or > 18%

### Phase 4: Enrichment Joins

Left-join AL leads to motivated seller and motivated renter data on `parcl_property_id`:
- Adds: motivated_seller_index_value, label, days_on_market, num_price_cuts, agent contact info
- Adds: motivated_renter_index_value, label, rental DOM, num_rent_reductions, property manager info

### Phase 5: Analysis

Compute and surface:
- **KPI metrics:** total leads, median list price, median rent, median/mean gross yield
- **Geographic distribution:** top ZIPs, top cities (bar charts)
- **Owner-occupied flag:** strongest PM pitch signal
- **Enrichment overlaps:** leads appearing in both motivated seller and renter data (double-signal)
- **Yield distribution:** sort leads by gross yield for actionable table ordering

### Phase 6: Dashboard Output

Build a single-file HTML dashboard. No external dependencies.

**Structure:**
- **Header:** Market name, date, total leads, "Parcl Labs MCP" branding
- **KPI strip:** Total leads, median list price, median rent, median gross yield, mean gross yield
- **Pitch angle insight box:** Gradient background card explaining why accidental landlords are ideal PM prospects
- **Distribution charts:** Top ZIPs and top cities as horizontal bar charts
- **Lead table:** Searchable, sortable table with columns: Address, Bed/Bath, Sq Ft, Year, Sale Price, Rent, Gross Yield, Owner-Occupied flag, Signals (motivated seller/renter badges). Sort by gross yield descending.
- **Methodology section:** Explain the 110-day window, same-owner filter, and outlier exclusions.

**Design:**
- Color palette: Blue (#2871CC), Orange (#E8841A), Dark Green (#1A2E1F)
- Clean, modern, minimal: white cards, subtle borders, sticky header
- Table max-height with scroll, sticky thead
- Search input for client-side row filtering

---

## Reference Output

See `examples/` for the Houston MSA reference implementation:
- `houston-dashboard.html`: complete dashboard (1,464 leads)
- `houston-timeseries.csv`: monthly AL rate data
- `houston-by-zip.csv`: ZIP-level granular analysis
- `houston-timeseries-chart.png` / `houston-by-zip-chart.png`: visualizations

See `reference/houston-methodology.md` for the exact reproduction methodology with validation against published benchmarks.

---

## Display Names

Never display raw `parcl_id` values in user-facing output. Always resolve to human-readable names:
- ZIP parcl_ids to actual ZIP codes and town names (e.g., `5452730` to "East Hampton (11937)")
- MSA parcl_ids to metro area names (e.g., `2900417` to "Tampa-St. Petersburg-Clearwater, FL")
- Investor IDs to standardized names from `search_investors`

Note: some MCP endpoints return IDs as floats with `.0` suffix (e.g., `5452730.0`). Strip the `.0` before any lookup or display.

---

## Quality Checks

Before delivering:
- [ ] All KPI values match the underlying data
- [ ] No outlier records in the table (check for implausible rents, yields)
- [ ] Search/filter works on the table
- [ ] Methodology section accurately describes what was done
- [ ] Gross yield calculation is correct: (rent x 12) / sale_price x 100
- [ ] Owner-occupied flag correctly sourced from property metadata
- [ ] Motivated seller/renter badges only appear when enrichment data exists for that property

---

## Adapting to Other Markets

This pipeline works for any MSA. High-value target markets (from published research): Houston, Dallas, Phoenix, Tampa, Atlanta, Charlotte. These six metros hold 36.8% of all large institutional SFR holdings and are where accidental landlord formation is accelerating fastest.
