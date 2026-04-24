---
name: property-manager-intel
description: Build a ranked rental property manager list with scale, geography, and contact info — separating third-party PMs, brokerages, institutional landlords, and listing platforms. Use for PM targeting or "who manages rentals in [market]".
user-invocable: true
argument-hint: "[market name or 'national']"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch
---

# Property Manager Intel

**Target:** $ARGUMENTS. Pass a market name (MSA, city, or ZIP) for a
single-market pull, or `national` for a nationwide list. If no argument
is given, ask the user which scope they want before proceeding.

## Trigger phrases

Invoke this skill on any of: "property manager list", "PM national list",
"PM coverage analysis", "property manager intelligence", "property
manager ranking", "rental property managers in [market]", "build PM
profiles", "PM targeting", "who manages rentals in [market]", or any
variant of "build/make/give me a PM list".

Produces a four-tab xlsx segmenting rental listings by the type of entity
doing the leasing. Third-party PMs, brokerages, institutional landlords,
and software / listing platforms are different businesses and are ranked
on separate tabs.

- **PM Profiles** — third-party property managers, including corporate-
  housing operators (Blueground, Nomad Homes). The main ranked list.
- **Brokerages** — Keller Williams, RE/MAX, Coldwell Banker, and similar
  real-estate brokerages. Their agents list rentals, but the brokerage
  itself does not manage rentals the way a PM does.
- **Institutional Landlords** — Invitation Homes, American Homes 4 Rent,
  Progress Residential, FirstKey, Tricon, and similar SFR operators that
  manage their own portfolios.
- **Rental Software & Platforms** — Zumper, AppFolio, Zillow, ShowMojo,
  and similar listing platforms and PM software. Visible as a separate
  leasing-activity surface rather than ranked alongside PMs.

## Workflow

### 1. Confirm scope

Ask the user: "Do you want a **national** PM list, or a **specific market**
(MSA, city, or ZIP)?"

- **Market** — resolve via `mcp__...__search_locations` with the user's
  query and `location_type` set if known (metro / city / zip / county).
  Use the returned `parcl_id` in the next step.
- **National** — do NOT pass `parcl_ids`. The endpoint treats an omitted
  `parcl_ids` array as "national search across all rentals".

### 2. Pull rental listings

Call the `motivated_renter_properties` MCP tool.

**IMPORTANT: `filters` is a nested object parameter. Pass it as a JSON
object — do NOT JSON-encode it as a string.** The tool will reject a
stringified filters value with a type error. Same for `parcl_ids`
inside filters: pass as an array of integers, not a string.

**Market scope — arguments to pass:**
- `filters`: `{"parcl_ids": [<resolved_parcl_id>], "limit": 50000, "offset": 0}`  (object, not string)
- `preview`: `false`  (boolean, not string)

**National scope — omit `parcl_ids` entirely:**
- `filters`: `{"limit": 50000, "offset": 0}`  (object, not string)
- `preview`: `false`

Two-step flow per batch:
1. Call once with `preview` set to `true` to see `estimated_records`
   and credit cost. For national, estimated_records is capped at
   `limit`, so it doesn't give you a true total — you have to paginate
   until exhausted.
2. Call with `preview` set to `false` to get a presigned `download_url`.
   Download the CSV (curl / requests — URL expires in 1 hour).

Paginate by incrementing `filters.offset` by `limit` until a batch
returns fewer than `limit` records. Save each batch CSV and concatenate.

Write the combined CSV to a working directory (e.g. `./pm_workspace/listings.csv`).

### 3. Run the pipeline

All four scripts declare dependencies inline via PEP 723, so `uv run`
resolves them automatically into an isolated environment — no venv
activation required. Prerequisite: `uv` installed
(`brew install uv` if not).

```bash
cd scripts/

uv run resolve_pm.py \
    --input ../pm_workspace/listings.csv \
    --output ../pm_workspace/resolved.csv

uv run dedup_pm.py \
    --input ../pm_workspace/resolved.csv \
    --output ../pm_workspace/deduped.csv

uv run build_profiles.py \
    --input ../pm_workspace/deduped.csv \
    --output ../pm_workspace/profiles.csv

uv run build_spreadsheet.py \
    --input ../pm_workspace/profiles.csv \
    --output ../pm_workspace/pm_list.xlsx
```

Each script prints a one-line summary — read it to verify counts look
reasonable before moving on.

If `uv` is unavailable, the scripts also work with a plain
`python3 <script>.py` invocation, provided `pandas`, `numpy`, and
`openpyxl` are importable from the active Python. No behavior
difference — the PEP 723 metadata is inert to the Python interpreter.

### 4. Clean up intermediate artifacts

Only the final xlsx is user-facing. After `build_spreadsheet.py` finishes
successfully, delete every intermediate CSV from `pm_workspace/` so the
directory contains only `pm_list.xlsx`:

```bash
rm -f ../pm_workspace/listings.csv \
      ../pm_workspace/resolved.csv \
      ../pm_workspace/deduped.csv \
      ../pm_workspace/profiles.csv
```

Do NOT delete anything if any upstream script errored — keep the
intermediates so you can inspect where the pipeline broke.

### 5. Deliver

Give the user:
- The xlsx file path.
- A short summary: unique PMs + unique listings per tab, top 5 third-party
  PMs by active rentals, top 3 institutional landlords by active rentals,
  and top 3 entities on the Rental Software tab.
- Any points from "How to Read This Output" below that apply.

## How Routing Works

The `company_type` column is the authoritative classification. Three
curated reference lists in `scripts/lib/blocklists.py` provide overlay
logic for cases the `company_type` column does not cover:

- **`RENTAL_SOFTWARE`** — routes listing platforms, PM software, and
  generic email-domain names to the Rental Software & Platforms tab.
- **`BROKERAGES`** — routes brand-name real-estate brokerages to the
  Brokerages tab.
- **`INSTITUTIONAL_LANDLORDS`** — routes named SFR operators to the
  Institutional Landlords tab and collapses spelling variants (e.g.
  "FirstKey Homes" / "FirstKeyHomes" / "Firstkey Homes, LLC") to a
  single canonical display name.

## PM Resolution Waterfall (7 tiers, first match wins)

Per listing row, these candidate fields are checked in priority order
(matches `scripts/resolve_pm.py` `resolve_row`):

1. `company_name` when `company_type` is `property_management` or
   `institutional_landlord`.
2. `property_manager` direct (when not a known rental-software override).
3. `company_name` fallback (any `company_type`, not software).
4. `agent_business` when `is_property_management_company == 1` (not
   software).
5. `agent_business` when `property_manager` is a known software /
   listing platform — the agent_business is the actual manager.
6. `agent_business` expanded (no PM flag required, not software) — the
   coverage-expansion tier that catches PMs missing from earlier tiers.
7. Last-resort: the first populated candidate *even if it's a software
   name*, so `categorize()` can still route the listing to the Rental
   Software tab. Software listings are segmented, not dropped silently.

## Categorization (which tab a listing lands on)

`company_type` is the primary routing signal. The overlay lists run as
a fallback when `company_type` is NaN or `other`.

`company_type` → tab:

| `company_type` | Tab |
|---|---|
| `property_management` | PM Profiles |
| `corporate_housing` | PM Profiles (Blueground, Nomad Homes, etc.) |
| `institutional_landlord` | Institutional Landlords |
| `brokerage` | Brokerages |
| `rental_software_platform` | Rental Software & Platforms |
| `listing_platform` | Rental Software & Platforms |
| `homebuilder` | filtered out (no PM signal) |
| `other` / NaN | fall through to override fallback |

Fallback (runs only when the primary table above does not match):

1. `entity_name` / `parent_company` matches an institutional alias →
   Institutional Landlords tab.
2. Resolved PM name matches an institutional alias → Institutional tab.
3. Resolved PM name matches `RENTAL_SOFTWARE` → Rental Software &
   Platforms tab.
4. Resolved PM name matches `BROKERAGES` → Brokerages tab.
5. Default → PM Profiles tab.

Whenever a listing routes to Institutional Landlords, its display name
is resolved to the canonical brand (e.g. "First Key Homes" and "FirstKey"
both display as "FirstKey Homes").

## How to Read This Output

A few things worth keeping in mind when working with the delivered xlsx:

1. **Institutional `active_rentals` = listings, not doors managed.** The
   numbers on the Institutional Landlords tab reflect *active rental
   listings* at the time of the pull. A large institutional operator may
   own tens of thousands of homes nationally with only a fraction actively
   listed at any given moment. The tab is a leasing-activity view, not a
   portfolio-size view.

2. **The Brokerages tab tracks leasing activity, not PM relationships.**
   Brokerages (Keller Williams, RE/MAX, Coldwell Banker, and similar)
   surface here because their agents list rentals. That's real market
   activity worth seeing, but it usually reflects an agent-of-record
   relationship rather than a third-party PM contract. Treat it as a
   distinct signal from the PM Profiles tab.

3. **The Rental Software & Platforms tab is a leasing-activity
   surface, not a PM directory.** Zumper, AppFolio, Zillow, and similar
   services appear here because their users list rentals through them.
   These are platforms facilitating listings, not property managers —
   the tab is here so the activity is visible without being ranked
   alongside PMs.

4. **Per-PM geography is based on active listings.** `num_states` /
   `num_msas` / `num_cities` / `num_zips` count where a PM currently
   has rentals listed, not where they operate. A PM with 5 cities this
   pull may operate in 20 — the active-listing snapshot is a lower
   bound.

5. **Contact-fill rates vary by source.** `representative_email` and
   `representative_phone` are populated where the listing carries agent
   contact info; fill rate is roughly 40-60% on third-party PMs and
   near-zero on institutional operators (who don't expose listing-agent
   contacts at the property level).

6. **The `primary_company_type` column is the authoritative classification.**
   Values include `property_management`, `brokerage`, `institutional_landlord`,
   `corporate_housing`, `rental_software_platform`, `listing_platform`, and
   `other`. Use this column to filter the PM Profiles tab to only rows
   explicitly classified as `property_management`.

## When the user asks to iterate

Common iterations after the first run:

- **"Too many brokerages in my third-party tab"** — identify the names,
  add their normalized form to `BROKERAGES`, re-run `resolve_pm` +
  downstream.
- **"Institutional X is missing"** — add to `INSTITUTIONAL_LANDLORDS` dict
  with alias set, re-run.
- **"I want just [one MSA] from an existing national pull"** — filter the
  listings CSV by `msa_name` or `msa_parcl_id` before running `resolve_pm`.

## Schema Notes

The pipeline expects these columns in the input CSV (from
`motivated_renter_properties`):

`parcl_property_id`, `latest_event_date`, `state`, `city`, `zip5`,
`msa_name`, `property_type`, `sq_ft`, `latest_listing_rent`,
`days_on_market`, `motivated_renter_index_value`,
`motivated_renter_index_label`, `algorithmic_pricing_detected`,
`property_manager`, `company_name`, `company_type`, `parent_company`,
`is_property_management_company`, `agent_name`, `agent_business`,
`agent_email`, `agent_phone`, `entity_name`, `investor_id`.

`company_type` values: `property_management`, `rental_software_platform`,
`brokerage`, `homebuilder`, `institutional_landlord`, `listing_platform`,
`corporate_housing`, `other`.

Each `parcl_property_id` appears at most once per pull.
