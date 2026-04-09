---
name: pool-service-targeting
description: New homeowner pool service leads with timing tiers and cluster routing
user-invocable: true
argument-hint: "[market name]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Pool Service — New Homeowner Targeting

Generates a route-optimized lead list of new homeowners who just purchased a home with a confirmed pool. Includes timing-based prioritization (hottest leads first), 80/20 zone clustering, and zone-level diagnostics for efficient door-to-door outreach.

**Target market:** $ARGUMENTS (defaults to Phoenix if not specified)

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
2. For metro areas, search multiple city names to capture suburban ZIPs. For Phoenix: also search Scottsdale, Tempe, Mesa, Chandler, Gilbert, Glendale, Peoria, Surprise.
3. Also search at `location_type: "metro"` for display name.
4. Collect all ZIP parcl_ids. Batch into groups of 5 or fewer per `property_events` call.

### Phase 2: Data Pull

Call `property_events` with:

- `parcl_ids`: batch of ZIP parcl_ids (max 5 per call)
- `event_names`: ["SOLD"]
- `property_types`: ["SINGLE_FAMILY"]
- `has_pool`: true
- `start_date`: 6 weeks before today (compute dynamically)
- `is_owner_occupied`: true
- `is_investor_owned`: false
- `include_property_details`: true
- `limit`: 50000

Always run `preview=True` first to check credit cost, then `preview=False` to download.

### Phase 3: Filter, Deduplicate & Tier Assignment

1. Download the CSV from the presigned URL.
2. Deduplicate to one row per `parcl_property_id`, keeping the most recent SOLD event.
3. Compute `days_since_sale` = today minus `event_event_date`.
4. Assign timing tiers:
   - **Strike Now**: 1-14 days since sale (highest conversion window)
   - **This Month**: 15-28 days since sale
   - **Follow-up**: 29-42 days since sale
5. Extract key fields: parcl_property_id, address, city, state, zip, lat, lng, sale_date, sale_price, year_built, beds, baths, sqft, timing_tier, days_since_sale.

### Phase 4: Density Grid & 80/20 Zone Assignment

1. **Build density grid**: Divide the bounding box of all qualifying properties into 0.5-mile square cells. Count properties per cell.

2. **Rank zones**: Sort cells by property count descending. Compute cumulative percentage.

3. **80/20 tier assignment**:
   - **Tier 1 (Red zone)**: top cells containing ~80% of all leads. Canvass these first.
   - **Tier 2 (Orange zone)**: next cells containing ~15%.
   - **Tier 3 (Blue zone)**: remaining sparse cells. Low priority.

4. **Assign each property** its zone cell ID and zone tier.

### Phase 5: Route Sequencing

Within each zone tier (Tier 1 first):

1. **Sort by timing tier first**: Strike Now leads before This Month before Follow-up within each zone.
2. **Within same timing tier**: nearest-neighbor traversal on lat/lng for walk-optimized order.
   - Start from the northernmost property.
   - At each step, move to the closest unvisited property (Euclidean distance).
3. **Chain zones**: after finishing one zone cell, move to the nearest unvisited cell.
4. Assign sequential `route_order` to each property.

### Phase 6: Output

Generate three deliverables:

**1. Interactive HTML Map (single-file, dark mode, Leaflet CDN)**

Use CARTO dark basemap tiles (`dark_all`). Dark theme throughout: background `#0f1117`, panels `#1a1d27` with `#2e3240` borders, text `#e4e6ed`, muted `#8b8fa3`. Zoom control at bottom-left.

**Zone rectangles** — crisp, grid-aligned:
- Tier 1: `#ef5350`, weight 2, fillOpacity 0.12
- Tier 2: `#ffa726`, weight 1.5, fillOpacity 0.08
- Tier 3: `#42a5f5`, weight 1, fillOpacity 0.04
- **Click a zone** → popup with full diagnostics:
  - Zone tier, total lead count, timing tier breakdown (Strike Now / This Month / Follow-up with color-coded counts)
  - Median sale price, median sqft
  - Scrollable property table (timing tier, address, ZIP, sale date, price, beds/baths) — dark styled, max-height 250px, timing tier text color-coded
  - Explanation sentence: "This zone is Tier 1 because it has X leads — in the top 80% by density. Y Strike Now leads make this a high-urgency canvass zone."

**Property dots**:
- radius: 4, fillOpacity 0.9, weight 1.5, stroke `rgba(255,255,255,0.4)`
- Strike Now: `#ef5350`
- This Month: `#ffa726`
- Follow-up: `#fdd835`
- Click popup: address, ZIP, sale date, days since sale, sale price, year built, beds/baths/sqft, timing tier, zone tier, route order

**Right side panel** — dark themed:
- KPI grid: Pool Home Leads, Delivery Zones, Median Sale Price, Median Sq Ft
- Timing — Contact Priority section: tier rows with colored left borders, descriptive subtitles ("Sold 1-14 days ago — highest conversion"), count badges
- Delivery Zones (80/20) section: zone tier rows with count and % stats
- Toggle checkboxes: Strike Now / This Month / Follow-up / Zones
- Insight box: "Sorted by zone tier (densest first), then timing (Strike Now before Follow-up), then nearest-neighbor walk order. Click any zone to see its leads and why it was prioritized."
- "Top Tier 1 Zones" why-box with lead counts and Strike Now counts
- **Lead List**: tabbed by timing tier (Strike Now / This Month / Follow-up), scrollable dark table (route#, timing, address, ZIP, sale date, price), timing column color-coded, click a row to pan map and open popup
- Footer: "Parcl Labs MCP · {date}"

**Dark-themed popups**: background `#1a1d27`, text `#e4e6ed`, border `#2e3240`.

**2. Master CSV**

Columns: route_order, zone_tier, timing_tier, days_since_sale, address, city, state, zip, sale_date, sale_price, year_built, beds, baths, sqft, has_pool, latitude, longitude

Sort by: zone_tier ASC, timing_tier priority (Strike Now=1, This Month=2, Follow-up=3), route_order ASC

**3. Per-timing-tier CSVs**

Same columns, split by timing tier:
- `strike_now_leads.csv` — 1-14 days, contact immediately
- `this_month_leads.csv` — 15-28 days, schedule visit
- `follow_up_leads.csv` — 29-42 days, mailer or call

---

## Quality Checks

Before delivering:
- [ ] All properties have `has_pool = true` (confirmed pools only)
- [ ] All sales within the specified recency window
- [ ] All properties are owner-occupied and not investor-owned
- [ ] Timing tiers correctly computed from sale date
- [ ] No raw parcl_ids in user-facing output
- [ ] Tier 1 zones contain approximately 80% of leads
- [ ] Route order follows geographic sequencing within each zone
- [ ] Zone click popups show property table and "why" explanation
- [ ] Lead list table in panel is tabbed by timing tier with click-to-pan
- [ ] Map uses dark mode with CARTO dark tiles
- [ ] CSV sort order: zone tier → timing tier → route order

---

## Adapting to Other Markets

This pipeline works for any metro with meaningful pool penetration. The `has_pool` flag is a confirmed attribute in the Parcl Labs data — not a proxy.

| Metro | Pool Prevalence | Best Season to Run |
|---|---|---|
| Phoenix | Very high | Feb-Mar (pre-summer ramp) |
| Las Vegas | Very high | Mar-Apr |
| Tampa / Orlando | High | Year-round (mild winters) |
| Houston / Dallas | High | Mar-Apr |
| Los Angeles | Moderate-high | Mar-May |
| Atlanta | Moderate | Apr-May |
