# Pool Service — New Homeowner Target List

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

I run a pool service company and need to find new homeowners who just bought a home with a pool. These are my highest-conversion leads because they don't have an existing service relationship. Using the Parcl MCP, build me a target list for Phoenix, AZ.

Steps:

1. Use `search_locations` to find Phoenix-area ZIP codes (search for "Phoenix" with location_type "zip" and state "AZ"). Also search for Scottsdale, Tempe, Mesa, Chandler, and Gilbert ZIPs to cover the full metro. Collect all ZIP-level parcl_ids.
2. Preview credit costs first, then pull property event data using `property_events` with these filters:
   - `parcl_ids`: all Phoenix-area ZIP parcl_ids (batch into groups of 5 max)
   - `event_names`: ["SOLD"]
   - `property_types`: ["SINGLE_FAMILY"]
   - `has_pool`: true
   - `start_date`: 6 weeks ago from today
   - `is_owner_occupied`: true
   - `is_investor_owned`: false
   - `include_property_details`: true
   - `limit`: 50000
3. Download the CSV. Deduplicate to one row per property (keep the most recent sale). Compute days since sale for each property and assign timing tiers:
   - "Strike Now" = sold 1-14 days ago (hottest leads)
   - "This Month" = sold 15-28 days ago
   - "Follow-up" = sold 29-42 days ago
4. Build a 0.5-mile density grid, rank zones by lead count, assign 80/20 zone tiers (Tier 1 = top 80% of leads, Tier 2 = next 15%, Tier 3 = rest).
5. Build a dark-mode interactive single-file HTML map using Leaflet (CDN is fine) with CARTO dark basemap tiles showing:
   - Zone rectangles color-coded by zone tier: Tier 1 = red (#ef5350), Tier 2 = orange (#ffa726), Tier 3 = blue (#42a5f5)
   - Clicking a zone shows a diagnostic popup with: lead count, timing tier breakdown, median sale price, a property table of all leads in that zone, and a sentence explaining why the zone was prioritized
   - All target properties as clickable circle markers color-coded by timing tier: Strike Now = red (#ef5350), This Month = orange (#ffa726), Follow-up = yellow (#fdd835)
   - Each dot popup shows: address, ZIP, sale date, days since sale, sale price, year built, beds/baths/sqft, timing tier, zone tier, route order
   - A dark side panel (#1a1d27 background) with: KPI grid (total leads, zones, median sale price, median sqft), timing tier breakdown, zone tier breakdown, toggle checkboxes, insight box, and a tabbed lead list table sorted by route order with click-to-pan
   - Dark-themed popups matching the panel
6. Export a CSV lead list with columns: route_order, zone_tier, timing_tier, days_since_sale, address, city, state, zip, sale_date, sale_price, year_built, beds, baths, sqft, has_pool, latitude, longitude. Sort by zone tier, then timing tier priority (Strike Now first), then route order.

Save the HTML map and CSV to the current working directory.
