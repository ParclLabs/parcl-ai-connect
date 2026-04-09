# Property Manager Fragmentation Analysis

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

Analyze property management fragmentation across Tampa's top SFR portfolios. Find every portfolio with at least 50 units in the Tampa metro. For each portfolio, pull their rental properties and break down which property managers handle their units.

Normalize PM names aggressively: strip LLC/Inc suffixes and consolidate known brand variants (e.g., "Main Street Renewal Llc" → "Main Street Renewal"). Group blank entries as "Unknown/Self-Managed."

Score each portfolio's PM concentration:
- Single PM: one PM manages everything
- Concentrated: top PM holds 85%+ share
- Fragmented: top PM holds 40-59%
- Highly Fragmented: top PM holds less than 40%

Flag fragmented portfolios with 50+ units as "High Opportunity": these are the best targets for pitching consolidated PM services.

Build a dark-themed interactive HTML dashboard with: KPI bar (portfolios analyzed, high/medium opportunity counts), portfolio ranking by opportunity signal, and an opportunity targets table with PM Mix visualizations showing colored segments per manager.

Exclude portfolios with 500+ units nationally: those are institutional self-managers.
