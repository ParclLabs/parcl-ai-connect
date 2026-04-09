---
name: hvac-direct-mail
description: Direct mail target list with route-optimized delivery zones for HVAC outreach
user-invocable: true
argument-hint: "[market name]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# HVAC / Home Services Direct Mail Targeting

Generates a route-optimized direct mail target list identifying aging, owner-occupied homes with long-tenure owners. Includes density-based clustering, 80/20 zone prioritization, original-owner flagging, and nearest-neighbor walk sequencing.

**Target market:** $ARGUMENTS (defaults to Houston if not specified)

---

## Display Names

Never display raw `parcl_id` values in user-facing output. Always resolve to human-readable names:
- ZIP parcl_ids to actual ZIP codes and town names
- MSA parcl_ids to metro area names

Note: some MCP endpoints return IDs as floats with `.0` suffix (e.g., `5452730.0`). Strip the `.0` before any lookup or display.

---

## Pipeline Steps

### Phase 1: Market Setup

1. Use `search_locations` to find all ZIP-level parcl_ids for the target market. Search with `location_type: "zip"` and the appropriate state abbreviation.
2. Also search at `location_type: "metro"` to get the MSA-level parcl_id for display purposes.
3. Collect all ZIP parcl_ids. For large metros, batch into groups of 5 or fewer per `property_events` call (API constraint).

### Phase 2: Data Pull

Call `property_events` with:

- `parcl_ids`: batch of ZIP parcl_ids (max 5 per call)
- `event_names`: ["ALL_SOLD"]
- `property_types`: ["SINGLE_FAMILY"]
- `max_year_built`: current year minus 10 (e.g., 2016 for 2026)
- `current_owner_occupied_flag`: true
- `current_on_market_flag`: false
- `include_property_details`: true
- `include_full_event_history`: true
- `limit`: 50000

Always run `preview=True` first to check credit cost, then `preview=False` to download.

### Phase 3: Filter, Deduplicate & Flag

1. Download the CSV from the presigned URL.
2. Filter to properties where `event_true_sale_index <= 2` (long-tenure owners with 2 or fewer lifetime sales).
3. Deduplicate to one row per `parcl_property_id`, keeping the most recent sale event.
4. **Flag original owners**: set `original_owner = TRUE` where `event_true_sale_index == 1`. These homes have never changed hands — the current owner is the original buyer, meaning the HVAC system has likely never been replaced.
5. Extract key fields: parcl_property_id, address, city, state, zip, lat, lng, year_built, beds, baths, sqft, lifetime_sales, original_owner.

### Phase 4: Density Grid & 80/20 Zone Assignment

1. **Build density grid**: Divide the bounding box of all qualifying properties into 0.5-mile square cells (~0.0072 degrees latitude, ~0.0087 degrees longitude at typical US latitudes). Count qualifying homes in each cell.

2. **Rank zones**: Sort cells by property count descending. Compute cumulative percentage of total properties.

3. **80/20 tier assignment**:
   - **Tier 1 (Red)**: top cells that collectively contain ~80% of all target properties. These are the "drop first" zones.
   - **Tier 2 (Orange)**: next cells containing the next ~15% of properties.
   - **Tier 3 (Blue)**: remaining cells with sparse coverage. Low priority.

4. **Assign each property** its zone cell ID and tier.

### Phase 5: Route Sequencing

Within each tier (starting with Tier 1):

1. Pick the zone cell with the most properties as the starting cell.
2. Within each cell, sort properties using nearest-neighbor traversal:
   - Start from the northernmost property.
   - At each step, move to the closest unvisited property (Euclidean distance on lat/lng).
   - This produces a walk-optimized delivery order.
3. Chain cells together: after finishing one cell, start the next nearest cell.
4. Assign a sequential `route_order` number to each property.

### Phase 6: Output

Generate three deliverables:

**1. Interactive HTML Map (single-file, dark mode, Leaflet CDN)**

Use CARTO dark basemap tiles (`dark_all`). Dark theme throughout: background `#0f1117`, panels `#1a1d27` with `#2e3240` borders, text `#e4e6ed`, muted `#8b8fa3`. Zoom control at bottom-left.

**Zone rectangles** — crisp, grid-aligned:
- Tier 1: `#ef5350`, weight 2, fillOpacity 0.12
- Tier 2: `#ffa726`, weight 1.5, fillOpacity 0.08
- Tier 3: `#42a5f5`, weight 1, fillOpacity 0.04
- **Click a zone** → popup with full diagnostics, **reactive to the Original Owner filter**:
  - Zone tier, visible home count (updates when owner filter changes), median year built, median sqft, % original owners
  - "(filtered)" badge when an owner filter is active
  - Scrollable property table (route#, address, ZIP, year built, beds/baths, sqft, owner type color-coded) — dark styled, max-height 250px. Table rows filter to match the active owner toggle.
  - Explanation sentence: "Tier 1 — top 80% by density. X homes visible, Y% original owners. Older vintage and high original-owner rate signal aging HVAC systems."

**Property dots** — small to avoid overlap:
- radius: 1.5, fillOpacity 0.8, weight 0.5, stroke `rgba(255,255,255,0.2)`
- Original Owner (1 sale): `#5b9cf6`
- Second Owner (2 sales): `#4dd0e1`
- Click popup: address, ZIP, year built, beds/baths/sqft, lifetime sales, original owner flag, tier, route order

**Right side panel** — dark themed:
- KPI grid: Total Homes, Delivery Zones, Median Year Built, Median Sq Ft
- Delivery Priority section: tier rows with colored left borders, count badges, % of targets
- Homeowner Tenure section: Original Owner count, Second Owner count
- Toggle checkboxes: Tier 1 / Tier 2 / Tier 3 / Zones / Original Owner / Second Owner. Unchecking "Second Owner" isolates to original owners only — dots disappear AND zone popups re-render to show only original-owner properties with updated counts and percentages.
- 80/20 Insight box: "Tier 1 captures X% of targets in Y% of zones"
- "Top 5 Tier 1 Zones" why-box with zone stats
- **Lead List**: tabbed by tier (Tier 1 / Tier 2 / Tier 3), scrollable dark table (route#, address, ZIP, built, beds/baths, sqft), click a row to pan map and open popup
- Footer: "Parcl Labs MCP · {date}"

**Dark-themed popups**: background `#1a1d27`, text `#e4e6ed`, border `#2e3240`.

**2. Master CSV**

Columns: route_order, tier, zone_id, address, city, state, zip, year_built, beds, baths, sqft, lifetime_sales, original_owner, latitude, longitude

Sort by: tier ASC, route_order ASC

**3. Per-tier CSVs** (optional, for splitting deliveries)

Same columns as master, one file per tier: `tier1_drop_first.csv`, `tier2_secondary.csv`, `tier3_low_priority.csv`

---

## Quality Checks

Before delivering:
- [ ] All properties are 10+ years old
- [ ] All properties are owner-occupied and not listed for sale
- [ ] All properties have 2 or fewer lifetime sales
- [ ] `original_owner` column correctly set to TRUE where lifetime_sales == 1
- [ ] No raw parcl_ids in user-facing output
- [ ] Tier 1 zones contain approximately 80% of target properties
- [ ] Route order within each zone follows geographic sequencing (no large jumps)
- [ ] Zone click popups show property table and "why" explanation
- [ ] Zone popups reactively filter when Original Owner / Second Owner toggle changes
- [ ] Lead list table in panel is tabbed by tier with click-to-pan
- [ ] Map uses dark mode with CARTO dark tiles
- [ ] CSV sort order matches route sequencing

---

## Adapting to Other Markets

This pipeline works for any metro. High-value HVAC markets by climate and housing age:

| Metro | Climate Driver | Avg Housing Age |
|---|---|---|
| Houston | Extreme heat, high humidity | 1970s-1990s boom |
| Phoenix | Extreme heat, desert dust | 1980s-2000s boom |
| Dallas | Extreme heat + winter freezes | 1970s-2000s |
| Tampa | Heat, humidity, salt air | 1960s-1990s |
| Atlanta | Heat + humidity + pollen | 1970s-2000s |
| Las Vegas | Extreme heat, desert dust | 1990s-2000s boom |
