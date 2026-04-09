# Portfolio Acquisition Targeting

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

Find SFR portfolios showing disposition signals in Louisville, Columbus, Memphis, and Birmingham that could be bulk acquisition targets.

Target criteria:
- 20-300 doors
- Average holding period of 10+ years
- Net Seller over the trailing 12 months
- At least 3 properties currently listed for sale

Use portfolio_search with progressive filter relaxation. Start with all four criteria, then relax progressively if no results (common in smaller metros). For each qualifying portfolio, pull their for-sale property details (listing price, DOM, price cuts, unrealized P&L, agent contact info) and full property list (for buy box computation).

Build an HTML dashboard with portfolio cards showing: criteria match score (X/4), buy box summary, market concentration, and a table of all for-sale listings with agent contact details. Sort by criteria match score descending.

Also export a CSV with one row per for-sale listing and portfolio metadata repeated on each row.

If no portfolios satisfy all four criteria, rank by best-fit and explain the market dynamics driving the gap.
