# Property Underwriter

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected. Replace the subject property address with your own.

---

I'm underwriting a residential property and need a full risk assessment dashboard.

Subject Property: 1097 Greenbriar Rd, Bethel Park, PA 15102

Important: verify the address match before underwriting (street number, street name, and ZIP against the returned record). If there is no exact match, show me your best-guess candidate with its property details and ask me to confirm it's the property I intended — never silently underwrite a different property or impute a value from neighbors.

Using the Parcl Labs MCP, please:

1. Price Index — Pull the Parcl Labs sale price index for the most granular geography available for this property (ZIP first, then county, then metro).
2. Last Sale Price — Look up the most recent transaction price for this specific property.
3. Imputed Current Value — Using the percent change in the price index from the last transaction date to today, impute the property's current estimated value.
4. Sale Comps — Within a 3-mile radius, pull the last 6 months of comparable sale transactions matched to the same product type (e.g., single-family). Filter out bulk/portfolio transfers priced well above market. Compute median price, median $/sqft, and the price distribution.
5. Rental Comps — Same radius and window, pull comparable rental listings and compute median monthly rent.
6. Risk Metrics — Compute gross rental yield (median annual rent / imputed value) and rent-to-value ratio, and compare the subject's implied $/sqft against the comp median.

Build a single-page, dark-themed HTML underwriting report with: a KPI row (imputed value, last sale price, estimated market rent, price index), a property details and valuation analysis section, a price index trend chart, a comp sale price distribution histogram, comp tables for sales and rentals, and a methodology and risk notes section.

Verify the imputed value and yield math before delivering, and note which price index geography was used.
