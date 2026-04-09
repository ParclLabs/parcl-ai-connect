---
name: market-study
description: Generate an institutional-grade market study PDF with price performance, supply-demand, and investor metrics
user-invocable: true
argument-hint: "[market name]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Market Study

Generates a comprehensive market study PDF for a target real estate market using Parcl Labs MCP data. Produces institutional-grade analysis with quarterly KPI matrices, supply-demand charts, and investor metrics.

**Target market:** $ARGUMENTS (e.g., "Hamptons", "Miami Beach", "Aspen")

**Audience:** Ultra-high-net-worth clients, luxury agents, and institutional investors.

---

## Tool Mapping

All tools are invoked through the Parcl Labs MCP server.

| Step | Tool | Purpose |
|------|------|---------|
| Resolve market | `search_locations` | Convert market name → parcl_id(s). Search metro, key ZIPs, cities. |
| Sale prices | `sale_price_index` | Price per sq ft over time |
| Rental prices | `rental_price_index` | Rental price trends |
| Gross yield | `rental_gross_yield` | Gross rental yields |
| New listing supply | `for_sale_new_listings_rolling_counts` | Rolling counts of new for-sale listings |
| Sales & listing counts | `market_metrics_housing_event_counts` | Total sales, new listings, rentals |
| Housing stock | `market_metrics_housing_stock` | Total housing stock |
| Investor acquisitions | `housing_event_counts` | Investor acquisitions vs dispositions |
| Ownership breakdown | `housing_stock_ownership` | Ownership breakdown by type |
| Net investor activity | `purchase_to_sale_ratio` | Purchase-to-sale ratio (apply 3-month rolling average) |
| Portfolio operator activity | `portfolio_sf_housing_event_counts` | SFR portfolio operator transactions |
| Portfolio ownership | `portfolio_sf_housing_stock_ownership` | Portfolio ownership share |
| All-cash share | `market_metrics_all_cash` | All-cash transaction percentage |
| Motivated seller scores | `motivated_seller_index` | Motivated seller scores by submarket |
| Listing-level seller data | `motivated_seller_properties` | Individual listings with price cut data |
| Property events (KPI matrices) | `property_events` | Full listing lifecycle for session reconstruction |
| Benchmarks | `search_locations` + above tools | Same metrics for parent MSA, state, USA |

For detailed tool notes, scope warnings, and the complete KPI matrix session reconstruction methodology, see [reference/analytical-framework.md](reference/analytical-framework.md).

---

## Execution Steps

1. **Resolve geography.** Use `search_locations` for metro area, then key ZIP codes and cities. Also resolve parent MSA, state, and USA aggregate for benchmarking.
2. **Preview all datasets.** Call each data tool with `preview=True` to check credit costs and record counts.
3. **Download datasets.** Call each data tool with `preview=False` for presigned CSV URLs (expire in 1 hour).
4. **Retrieve CSVs.** Download each CSV via presigned URLs.
5. **Generate PDF.** Produce the full report following the structure below.

---

## PDF Structure

1. **Cover Page**: Market name, date, Parcl Labs branding. Disclaimer about data sources.
2. **Executive Summary**: Current price level/YoY, supply-demand gap, price cut rate vs 41% national benchmark, market classification, top risk and opportunity.
3. **Price Performance**: Sale price index chart with submarket lines + metro benchmark. Submarket price table.
4. **Key Market Indicators**: Institutional KPI matrices:
   - All Properties matrix (QoQ and YoY comparisons)
   - Single Family matrix
   - Luxury segment matrix (top 10% by price)
   - Listing distribution by price tier
5. **Supply-Demand Dynamics**: KPI boxes, divergence chart (Jan 2023 onward), gap interpretation.
6. **Seller Behavior & Motivated Sellers**: Bubble chart (X=DOM, Y=cut rate, size=listings, color=MSI label), operational metrics table.
7. **All-Cash Transactions**: Share over time, flows into investor section.
8. **Investor Activity**: Acquisitions vs dispositions, purchase-to-sale ratio, ownership chart.
9. **Portfolio Operator Activity**: SFR operator trends, institutional presence.
10. **Market Outlook**: Forward-looking synthesis.
11. **Appendix**: Data dictionary, methodology, attribution.

---

## Display Names

Never display raw `parcl_id` values in user-facing output. Always resolve to human-readable names:
- ZIP parcl_ids to actual ZIP codes and town names (e.g., `5452730` to "East Hampton (11937)")
- MSA parcl_ids to metro area names (e.g., `2900417` to "Tampa-St. Petersburg-Clearwater, FL")
- Investor IDs to standardized names from `search_investors`

Note: some MCP endpoints return IDs as floats with `.0` suffix (e.g., `5452730.0`). Strip the `.0` before any lookup or display.

---

## Narrative Style

Follow the Parcl Labs Annual Housing Report voice:
- State the finding first, then support with specific numbers
- Use precise figures, not hedging language
- Compare to benchmarks: national averages, prior year, historical norms
- Flag inflection points and divergences between metrics

**Anti-AI writing rules (mandatory):**
1. No significance inflation ("significant," "crucial," "vital," "notably")
2. No promotional language ("impressive," "remarkable," "robust")
3. No copula hedging ("stands at," "sits at," "comes in at")
4. No -ing analysis starters ("Highlighting...", "Underscoring...")
5. No rule-of-three lists. Vary structure
6. No em dashes in narrative prose (use commas, parentheses, periods)
7. No bold inline headers in body text
8. Vary sentence length. Mix short and long
9. Use contractions where natural
10. Every paragraph has a clear takeaway

---

## Visualization Principles

- Every chart title states the takeaway, not just the metric
- Horizontal text always; never rotate axis labels
- Direct-label lines/bars instead of legends when possible
- Source attribution on every chart ("Source: Parcl Labs")
- Colorblind-friendly palettes
- No 3D or pie charts
