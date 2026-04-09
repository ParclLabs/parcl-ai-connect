# Market Study

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

Generate a comprehensive market study for the Hamptons real estate market using Parcl Labs data. Search for the Hamptons area and key ZIP codes within it, plus the parent MSA and USA aggregate for benchmarking.

Pull these datasets:
- Sale price index and rental price index for price trends
- Market metrics housing event counts for supply/demand (both ALL_PROPERTIES and SINGLE_FAMILY)
- Housing stock and ownership breakdown
- Purchase-to-sale ratio (apply 3-month rolling average before charting)
- Motivated seller index and properties for seller behavior analysis
- All-cash transaction percentage
- Portfolio operator activity

Build a PDF-style report covering:
1. Executive summary with market classification (buyer's/seller's/balanced)
2. Price performance with submarket comparisons
3. Supply-demand gap analysis (new listings vs sales, 3-month MA of YoY changes)
4. Seller behavior bubble chart (X=DOM, Y=price cut rate, size=listings, color by motivated seller label)
5. Investor activity and ownership trends
6. Market outlook

Use precise numbers, not hedging language. Compare everything to the 41% national price cut rate benchmark. State findings first, then support with data.
