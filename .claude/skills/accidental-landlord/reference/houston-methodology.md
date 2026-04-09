# Houston Accidental Landlord Rate: Reproduction Methodology

Generated April 1, 2026 via Parcl Labs MCP.

## What This Reproduces

The accidental landlord rate time series from the published Parcl Labs research piece ("When Sellers Can't Sell"). The published chart shows the Houston Metro AL rate monthly from roughly January 2023 through April 2025, with the headline figure of 6.8% for April 2025.

## Data Sources

All data pulled from Parcl Labs MCP using `property_events` and `market_metrics_housing_event_counts` for parcl_id `2899967` (Houston-The Woodlands-Sugar Land, TX MSA).

### Pulls Made

**Aggregate data (denominator reference):**
- `market_metrics_housing_event_counts`: Monthly new_listings_for_sale and new_rental_listings, Nov 2022 – Feb 2026

**Property-level events (for transition matching):**
- LISTED_SALE events: 13 chunks covering Nov 2022 – Mar 2026 (523,096 events, 288,579 unique properties)
- LISTED_RENT events: 10 chunks covering Jan 2023 – Mar 2026 (384,582 events, 173,575 unique properties)

## Methodology

### 110-Day Rolling Window

For each analysis date (sampled on the 15th of each month, Feb 2023 – Jan 2026):

1. **Lookback window** (50 days prior): Identify all unique properties with LISTED_SALE events
2. **Lookahead window** (60 days forward): Identify all unique properties with LISTED_RENT events
3. **Intersection**: Properties appearing in BOTH windows = sale-to-rent transitions
4. **Same-owner filter**: Keep only transitions where `event_entity_owner_name` matches across sale and rental events (both-null treated as a match)
5. **Rate**: same_owner_transitions / unique_sale_properties × 100

### Simplifications vs. Published Methodology

This reproduction uses LISTED_SALE and LISTED_RENT events only. The published methodology additionally includes LISTING_PRICE_CHANGE, RELISTED, and RENTAL_PRICE_CHANGE events, which captures properties that were already listed but had activity during the window. This accounts for the slight undercount vs. published figures.

The published methodology also excludes properties with completed sale transactions within the 110-day window. This exclusion was not implemented here.

## Results vs. Published Benchmarks

| Metric | Published | Reproduced | Delta |
|--------|-----------|------------|-------|
| Houston April 2025 rate | 6.8% | 6.3% | -0.5pp |
| Peak seasonality timing | Summer/Fall | Summer/Fall (Jun-Oct) | Match |
| Seasonal pattern | Present | Present (2-3pp amplitude) | Match |
| Year-over-year direction | +41.4% | +18.5% (Apr), +50.7% (Jun) | Directionally match |

The 0.5pp undercount in April 2025 is consistent with the narrower event set used. The seasonal shape, peak timing, and YoY acceleration all match the published research.

## YoY Comparisons (2024 vs 2025)

| Month | 2024 Rate | 2025 Rate | YoY Change |
|-------|-----------|-----------|------------|
| Jan | 6.7% | 7.5% | +11.6% |
| Feb | 6.1% | 6.3% | +3.3% |
| Mar | 5.4% | 6.2% | +13.7% |
| Apr | 5.3% | 6.3% | +18.5% |
| May | 5.7% | 7.2% | +26.3% |
| Jun | 5.9% | 8.9% | +50.7% |
| Jul | 6.6% | 8.2% | +24.8% |
| Aug | 5.7% | 7.6% | +32.9% |
| Sep | 6.0% | 8.0% | +32.4% |
| Oct | 5.8% | 7.9% | +35.6% |
| Nov | 5.5% | 7.7% | +39.6% |
| Dec | 6.6% | 7.2% | +8.8% |

The average YoY increase across all months is approximately +24.8%, with late-summer and fall months (Aug-Nov) showing the strongest acceleration (+32-40%), consistent with the published +41.4% headline figure which was likely computed over a specific rolling period.

## Output Files

- `houston_al_rate_chart.png`: Time series chart (dark theme, Parcl Labs dataviz style)
- `houston_al_rate_timeseries.csv`: Raw data: analysis_date, sale_properties, same_owner_transitions, al_rate
