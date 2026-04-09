# Analytical Framework: Parcl Labs Housing Intelligence Methodology

## Scope Warnings

- **Listing counts differ between tools:** `motivated_seller_properties` is filtered to specific ZIP codes and returns a smaller set. `motivated_seller_index` covers the full county. When both appear on the same page, include a footnote clarifying the geographic scope difference.
- **Purchase-to-sale ratio chart:** Always apply a 3-month rolling average before plotting to smooth month-to-month volatility.
- There is no dedicated `for_sale_inventory` tool. Use `for_sale_new_listings_rolling_counts` as the supply-side proxy. Supplement with `market_metrics_housing_event_counts` for absolute counts. Use `motivated_seller_properties` for active listing inventory and price tier breakdowns.

---

## KPI Matrix Session Reconstruction

The `motivated_seller_properties` tool returns a current snapshot only. To fill every cell in the KPI matrices (including historical inventory, DOM, price cut rate, and months of supply), use listing session reconstruction:

1. **Pull full lifecycle events** from `property_events` with `event_names: ["SOLD", "LISTED_SALE", "PRICE_CHANGE", "LISTING_REMOVED", "PENDING_SALE", "RELISTED"]` and a date range covering at least 2 years.
2. **Reconstruct listing sessions** by grouping events per property: a session starts with `LISTED_SALE` or `RELISTED` and ends with `SOLD` or `LISTING_REMOVED`. `PRICE_CHANGE` events within a session count as price cuts. Sessions still open at analysis time are tagged `ACTIVE`.
3. **Compute quarterly metrics:**
   - **Sales counts & prices**: Use raw `SOLD` events directly (more complete than session-based).
   - **New listings**: Count `LISTED_SALE` events per quarter.
   - **Inventory at quarter end**: Count sessions where `list_date <= quarter_end AND close_date > quarter_end`.
   - **Median DOM at quarter end**: For active sessions at quarter end, compute `quarter_end - list_date` in days.
   - **Price cut rate at quarter end**: Among active sessions at quarter end, percentage with `num_price_changes > 0`.
   - **Months of supply**: `inventory_at_quarter_end / (quarterly_sales / 3)`.
4. **QoQ and YoY deltas**: Compare current quarter to prior quarter and same quarter one year ago for every metric.

---

## Real-Time Market Conditions

- **Price Growth YoY**: Current price feed reading vs same date one year prior.
- **Year-to-Date Price Growth**: Current reading vs January 1 of current year.
- **Peak Value to Current**: Highest point from January 1, 2020 onward. Determines correction status.
- **Change since COVID**: Current reading vs February 1, 2020 baseline.

## Supply-Demand Gap (3-Month Moving Average Method)

- **Supply** = total new single-family listings for sale (monthly, from `market_metrics_housing_event_counts` with `property_type: SINGLE_FAMILY`)
- **Demand** = total single-family properties sold (same source)
- Compute YoY change for both, apply 3-month moving average, then Gap = supply MA - demand MA.
- **Surplus**: New listings minus sales for a given month.
- **Absorption Rate**: Sales divided by new listings, as percentage.

**Divergence chart:** Supply bars up, demand bars down (positive absolute values on y-axis). Red line on secondary axis tracks 3-month rolling gap percentage. Truncate to January 2023 onward. Quarterly x-axis ticks with `"%b\n'%y"` format.

**Gap interpretation thresholds:**

| Gap | Classification | Price Pressure |
|-----|---------------|----------------|
| > +30% | Severe buyer's market | Strong downward |
| +15% to +30% | Moderate buyer's market | Moderate downward |
| -5% to +15% | Roughly balanced | Neutral |
| < -5% | Seller's market | Upward |

## Market Correction Definitions

- **Bear Market**: -20% or more from peak
- **Correction Territory**: -10% to -20% from peak
- **Approaching Correction**: -5% to -10% from peak

## Market Rating

- **Bullish**: YoY price growth > 3% AND negative market gap
- **Bearish**: Negative YoY price growth OR market gap above +30%
- **Neutral**: All other conditions

## Investor Metrics

- **Purchase-to-Sale Ratio**: Acquisitions / dispositions. Chart as 3-month rolling average.
- **All Investor Market Share**: % of housing stock owned by investors.
- **Large Institutional Share**: % owned by portfolios of 1,000+ properties.
- **Gross Yield**: (Monthly median rental price x 12) / median listing sale price.

## Seller Behavior Benchmarks

| Price Cut Rate | Signal |
|---|---|
| > 45% | Aggressive seller adjustment, prices likely to fall further |
| 41% (national avg) | Benchmark |
| 30-41% | Moderate pressure, market-dependent |
| < 30% | Seller confidence, prices well supported |

## Market Classification

- **Severe stress**: Gap > +30%, price cuts > 45%, negative MoM prices
- **Moderating**: Gap narrowing from peak, price cuts elevated but stable
- **Balanced**: Gap near 0%, price cuts ~30%, flat prices
- **Tight / Appreciating**: Negative gap, price cuts < 30%, positive MoM prices

## Page Layout

- **Hard page breaks before**: Executive Summary, Price Performance, Key Market Indicators, Supply-Demand Dynamics, Seller Behavior, Appendix
- **Soft flow between**: All-Cash Transactions → Investor Activity, Investor charts flow continuously, Ownership chart → Market Outlook
- **Chart sizing**: width=6.5*inch. Heights: supply-demand and investor charts at 3.25*inch, seller bubble chart at 3.85*inch
