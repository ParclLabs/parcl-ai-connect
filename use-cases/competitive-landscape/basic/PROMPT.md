# Competitor Portfolio Analysis

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

Build a comprehensive portfolio analysis of a target institutional SFR investor using Parcl Labs Portfolio Hunter. Search for the investor by name to get their investor_id, then pull their MSA-level activity to find their top 10 markets by property count.

Create an Excel workbook with these tabs:
1. **Portfolio Overview**: National summary and market breakdown sorted by property count
2. **Rental Price Index**: Monthly $/sqft/month for top 10 markets (2020-present)
3. **Buy Box**: Per market: P10/Median/P90 for sqft, beds, baths, year built, acquisition price
4. **Acquisitions vs Sales**: By market and year: purchase count, sale count, net activity, avg prices
5. **Availability**: Active rentals and for-sale listings per market with DOM and pricing
6. **For-Sale Detail**: Property-level detail for all listed-for-sale units
7. **Investor vs Market Rents**: Compare their $/sqft/month to the Parcl Labs Rental Price Index
8. **Algo Pricing**: Classify rentals as algo-priced if they use a centralized leasing email or have 3+ price changes

Use professional formatting: dark blue headers, green/red conditional coloring, freeze panes, and national rollup rows with light blue fill.
