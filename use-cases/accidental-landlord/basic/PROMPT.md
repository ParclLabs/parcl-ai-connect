# Accidental Landlord Lead Generation

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

Build an accidental landlord lead gen pipeline for the Houston metro area. Accidental landlords are homeowners who failed to sell and pivoted to renting. They're the highest-intent property management prospects.

Steps:
1. Use `search_locations` to find the Houston MSA parcl_id
2. Pull for-sale listing events (LISTED_SALE, LISTING_PRICE_CHANGE, RELISTED) for single-family homes from 4-5 months ago to ~45 days ago
3. Pull rental listing events (LISTED_RENT, RENTAL_PRICE_CHANGE) for single-family homes from ~45 days ago to today
4. Find properties that appear in BOTH datasets (sale-to-rent transitions) where the owner name matches across events
5. Filter outliers: remove rents below $500 or above $10K, sale prices below $50K, and gross yields outside 2-18%
6. Pull the top 500 motivated sellers and top 500 motivated renters for enrichment
7. Build a single-file HTML dashboard with: KPI strip (total leads, median price, median rent, median yield), geographic distribution charts, and a searchable lead table sorted by gross yield

Use blue (#2871CC), orange (#E8841A), and dark green (#1A2E1F) for the color palette.
