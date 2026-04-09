Tampa Property Manager Fragmentation Analysis
Identify fragmented property management relationships across Tampa's top single-family rental portfolios, surfacing portfolio owners who may benefit from consolidated PM services.

The Ask
In the Tampa metro area, find every portfolio with at least 50 units. For each portfolio, break down their for-rent exposure by property manager to determine whether the owner has a clear, consolidated relationship with one PM company, or whether the relationship is fragmented across multiple managers. Fragmented portfolios represent a direct opportunity to pitch unified property management services.
Exclude portfolios with more than 500 units nationally. These are institutional operators who self-manage or have locked-in PM relationships.

How It Works
1. Identify the Tampa Market
Search for the Tampa metro area in Parcl Labs to resolve the parcl ID. This is the anchor market for the entire analysis.
2. Find Every 50+ Unit Portfolio in Tampa
Run a portfolio search across the Tampa MSA filtered to a minimum of 50 units. This captures institutional and mid-size operators, the portfolios large enough to need professional management but small enough that they may not have it figured out yet.
3. Pull Rental Property Data with PM Details
Download rental listings for every portfolio identified. The key fields are enhanced_manager_agent_business and enhanced_manager_property_manager. These reveal who is actually managing each rental unit on behalf of the portfolio owner.
4. Normalize PM Names
Raw data contains dozens of variants for the same PM company (e.g., "Main Street Renewal", "Main Street Renewal Llc", "Main Street Renewal, Llc" are all the same firm). Normalize aggressively: strip LLC/Inc suffixes, consolidate known brand variants, and group blank/missing entries as "Unknown/Self-Managed." This step is critical; without it, portfolios appear far more fragmented than they actually are.
Common normalization examples:

"American Homes 4 Rent" / "Amh (American Homes 4 Rent)" / "Amh.Com" → American Homes 4 Rent
"Firstkey Homes" / "Firstkey Homes, Llc" / "Firstkey Homes Llc" → FirstKey Homes
"Darwin Homes" / "Darwin Homes, Llc." / "Darwin Properties" → Darwin Homes
"Mynd" / "Mynd Property Management" / "Mynd Management" → Mynd
"Tricon Residential" / "Tricon" / "Tah [State] Llc" → Tricon Residential

5. Score PM Concentration
For each portfolio, calculate the share of known-PM-managed units held by each property manager. Classify:

Single PM: one PM manages everything
Concentrated: top PM holds 85%+ share
Moderately Concentrated: top PM holds 60-84%
Fragmented: top PM holds 40-59%
Highly Fragmented: top PM holds less than 40%
Self-Managed/Unknown: no identifiable PM at all

Score opportunity level:

High: Fragmented or Highly Fragmented with 50+ rental units in the market
Medium: Same classification with 20-49 units, or Self-Managed/Unknown with 50+ units
Low-Medium: Moderately Concentrated with 3+ PMs and 50+ units

6. Build the Dashboard
Produce a single interactive HTML file (dark theme, all text bright white for readability) with:

KPI bar: portfolios analyzed, total rental units covered, high-opportunity count, medium-opportunity count
Portfolio summary: ranked list of all Tampa portfolios by opportunity signal then size, with classification badges and unit counts
Opportunity targets table: filterable by signal level. Columns: Owner, Rental Units, # of PMs, PM Mix (inline colored segments with hover tooltips), Top PM, Top PM Share, 2nd PM, 2nd PM Share, Classification, Opportunity Signal.
Portfolio drill-down: clickable rows expanding to show full PM breakdown per portfolio with unit counts and share percentages.

No Unknown % column. It adds noise without changing the signal.

Data Sources
All data sourced from Parcl Labs Portfolio Hunter:

search_locations: resolve parcl IDs to metro names
portfolio_search: find portfolios by market and size criteria
investor_rental_properties: property-level rental data with PM company details
