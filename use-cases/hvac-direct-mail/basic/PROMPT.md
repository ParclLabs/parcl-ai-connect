# HVAC Direct Mail Target List

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

I'm running a direct mail flyer campaign targeting homeowners who are likely to need HVAC services. Using the Parcl MCP, build me a tightened target list for Houston, TX.

Steps:

1. Use `search_locations` to find all Houston-area ZIP codes (search for "Houston" with location_type "zip" and state "TX"). Collect all ZIP-level parcl_ids.
2. Preview credit costs first, then pull property event data using `property_events` with these filters:
   - `parcl_ids`: all Houston ZIP parcl_ids (batch into groups of 5 max)
   - `event_names`: ["ALL_SOLD"]
   - `property_types`: ["SINGLE_FAMILY"]
   - `max_year_built`: 2016
   - `current_owner_occupied_flag`: true
   - `current_on_market_flag`: false
   - `include_property_details`: true
   - `include_full_event_history`: true
   - `limit`: 50000
3. Download the CSV and filter to properties with `event_true_sale_index` of 2 or fewer (long-tenure owners). Deduplicate to one row per property, keeping the most recent sale event. Flag properties with `event_true_sale_index` equal to 1 as "Original Owner" — these are the highest-priority targets because their HVAC system has never been replaced by a previous buyer.
4. Find the densest geographic cluster: compute a 0.5-mile density grid across all qualifying properties, identify the cell with the highest concentration, and pull all qualifying homes within a 3-mile radius of that center point.
5. Build a dark-mode interactive single-file HTML map using Leaflet (CDN is fine) with CARTO dark basemap tiles showing:
   - All target properties as small clickable circle markers (radius ~1.5 to avoid overlap)
   - Color-coded by owner type: Original Owner (1 sale) = blue (#5b9cf6), Second Owner (2 sales) = teal (#4dd0e1)
   - A dashed circle overlay showing the 3-mile search radius
   - Each dot popup shows: address, ZIP, year built, beds/baths/sqft, lifetime sales, original owner flag
   - A dark side panel (#1a1d27 background) with: KPI grid (total homes, ZIP count, median year built, median sqft), tenure breakdown showing Original Owner vs Second Owner counts, and an insight box explaining the target criteria
   - Dark-themed popups matching the panel
6. Export a CSV direct mail list with columns: address, city, state, zip, year_built, beds, baths, sqft, lifetime_sales, original_owner, latitude, longitude. The `original_owner` column should be TRUE when lifetime_sales equals 1. Sort by ZIP code then street address.

Save the HTML map and CSV to the current working directory.
