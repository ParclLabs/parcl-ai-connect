# Broker Analytics: Motivated Seller Analysis

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

Analyze broker and agent performance across listings in the Hamptons market.

To adjust the segment, change the price threshold below. Use $2,000,000 for luxury, $500,000 for mid-market, or remove the filter entirely to analyze the full market.

Steps:
1. Use `search_locations` to find all relevant Hamptons ZIP codes and parcl_ids
2. Pull `motivated_seller_properties` for all those IDs, sorted by latest_listing_price descending, limit 50000: preview first to check credit cost, then download
3. Filter to properties where latest_listing_price > $2,000,000 (adjust this threshold as needed)
4. Build a 5-sheet Excel workbook:
   - **Executive Summary**: market snapshot KPIs (total listings, unique brokerages, unique agents, median price, avg DOM, avg motivated seller score, label distribution)
   - **All Properties**: every listing sorted by motivated seller score descending with full details (address, price, DOM, price cuts, agent, brokerage, contact info)
   - **Brokerage Analysis**: aggregate by brokerage, ranked by avg motivated seller score (worst performers at top), with "vs Market Avg" delta column
   - **Agent Analysis**: aggregate by agent + brokerage, same ranking and delta logic
   - **Fire Sale & Motivated Detail**: only fire_sale and motivated properties with agent/brokerage contact info

Use dark navy title bars (#1F4E79), highlight fire_sale rows in light red (#FFC7CE), motivated rows in light yellow (#FFEB9C), and brokerages/agents scoring above market average in cream (#FFF2CC). Format the "vs Market Avg" cells with red text for positive (underperforming) and green for negative (outperforming).
