# Property Manager Intel

Copy and paste this prompt into Claude Code with the Parcl Labs MCP connected.

---

Build a ranked list of rental property managers for the Phoenix MSA, separating third-party property managers from brokerages, institutional landlords, and listing platforms so I never confuse them.

Steps:

1. Use `search_locations` to resolve "Phoenix" to a `parcl_id` (metro / MSA).
2. Call `motivated_renter_properties` with `filters` as an OBJECT (not a string): `{"parcl_ids": [<parcl_id>], "limit": 50000, "offset": 0}` and `preview: false`. Paginate by bumping `filters.offset` by `limit` until a batch returns fewer rows than the limit.
3. For each listing, pick a PM name using this waterfall (first match wins):
   1. `company_name` when `company_type` is `property_management` or `institutional_landlord`
   2. `property_manager` (skip if it's a known listing platform like Zumper / AppFolio / Zillow)
   3. `company_name` fallback
   4. `agent_business` when `is_property_management_company == 1`
   5. `agent_business` when `property_manager` is a listing platform (the agent is the real PM)
   6. `agent_business` fallback
4. Categorize each listing into a tab using `company_type` first:
   - `property_management` or `corporate_housing` → PM Profiles
   - `brokerage` → Brokerages
   - `institutional_landlord` → Institutional Landlords
   - `rental_software_platform` or `listing_platform` → Rental Software & Platforms
   - `homebuilder` → drop
   - NaN / `other` → fall back to name-based matching: institutional operators (Invitation Homes, AMH, Progress Residential, FirstKey, Tricon, Main Street Renewal, Amherst, VineBrook, Maymont, Blackstone, etc.) → Institutional; rental software (Zumper, AppFolio, ShowMojo, TenantTurner, generic email domains like gmail/yahoo/outlook) → Rental Software; brokerages (Keller Williams, RE/MAX, Coldwell Banker, Compass, Century 21, eXp, Sotheby's, Berkshire Hathaway, Douglas Elliman, Redfin, etc.) → Brokerages; default → PM Profiles.
5. Collapse institutional name variants to their canonical display (e.g. "First Key Homes" / "FirstKey" / "FKH" all become "FirstKey Homes").
6. Normalize PM names (lowercase, strip legal suffixes like LLC/Inc, collapse whitespace) and group by the normalized key. For each group, pick the most-frequent raw variant as the display name.
7. For each PM, aggregate: active rentals, states + count, top 5 MSAs, unique cities, unique ZIPs, avg/median rent, avg sqft, avg/median DOM, property-type mix, motivated-renter index (avg value + share desperate-to-lease), algo-pricing share, representative email (prefer legitimate addresses over syndication relays like `@rentalbeast.com`, `@move.com`, `*+syndication+*@email1.showmojo.com`), representative phone, and contact fill rate.
8. Write the output as a single xlsx with five tabs:
   - **Summary** — one row per category with unique PMs and unique listings
   - **PM Profiles** — third-party PMs, sorted by active rentals desc
   - **Brokerages** — sorted by active rentals desc
   - **Institutional Landlords** — sorted by active rentals desc
   - **Rental Software & Platforms** — sorted by active rentals desc

Style each tab with a dark blue header row (`#1F4E78`), white bold header text, frozen header row, autofilter across all columns, and sensible column widths (wider for name / states / top MSAs / email).

Confirm the scope with me before kicking off if there's any ambiguity on the market.
