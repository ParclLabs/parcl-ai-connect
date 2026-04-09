# Accidental Landlord Lead Gen: Session Methodology & Results

Generated April 1, 2026 from a Cowork session running the Parcl Labs MCP against the Houston MSA.

## What We Built

An end-to-end lead gen pipeline that identifies accidental landlords (homeowners who failed to sell and pivoted to renting) and packages them into an actionable dashboard for property services firms. The Houston MSA case study produced 1,464 qualified leads.

## MCP Tools Used

### Step 1: Location Lookup
- **Tool:** `search_locations`, query "Houston metro", location_type "metro"
- **Result:** parcl_id `2899967` (Houston-The Woodlands-Sugar Land, TX)

### Step 2: For-Sale Listing Events
- **Tool:** `property_events`
- **Filters:**
  - `parcl_ids`: [2899967]
  - `event_names`: ["LISTED_SALE", "LISTING_PRICE_CHANGE", "RELISTED"]
  - `start_date`: "2025-11-01"
  - `end_date`: "2026-02-15"
  - `property_types`: ["SINGLE_FAMILY"]
  - `include_property_details`: true
  - `limit`: 20000
- **Result:** 36,385 sale listing events across 20,000 unique properties

### Step 3: Rental Listing Events
- **Tool:** `property_events`
- **Filters:**
  - `parcl_ids`: [2899967]
  - `event_names`: ["LISTED_RENT", "RENTAL_PRICE_CHANGE"]
  - `start_date`: "2026-01-01"
  - `end_date`: "2026-04-01"
  - `property_types`: ["SINGLE_FAMILY"]
  - `include_property_details`: true
  - `limit`: 20000
- **Result:** 39,904 rental events across 20,000 unique properties

### Step 4: Enrichment, Motivated Seller Properties
- **Tool:** `motivated_seller_properties`
- **Filters:**
  - `parcl_ids`: [2899967]
  - `property_types`: ["SINGLE_FAMILY"]
  - `limit`: 500
  - `sort_by`: "motivated_seller_index_value"
  - `sort_order`: "desc"
- **Result:** 500 most motivated sellers in Houston, joined to AL leads on parcl_property_id

### Step 5: Enrichment, Motivated Renter Properties
- **Tool:** `motivated_renter_properties`
- **Filters:**
  - `parcl_ids`: [2899967]
  - `property_types`: ["SINGLE_FAMILY"]
  - `limit`: 500
  - `sort_by`: "motivated_renter_index_value"
  - `sort_order`: "desc"
- **Result:** 500 most motivated rental listings, joined to AL leads on parcl_property_id for current rental market signals

## 110-Day Rolling Window Methodology

For each analysis date (sampled every 15 days from Dec 15 2025 to Feb 15 2026):

1. **Lookback window** (50 days prior): Pull all properties with for-sale events (LISTED_SALE, LISTING_PRICE_CHANGE, RELISTED)
2. **Lookahead window** (60 days forward): Pull all properties with rental events (LISTED_RENT, RENTAL_PRICE_CHANGE)
3. **Intersection**: Properties appearing in BOTH windows = sale-to-rent transitions
4. **Same-owner filter**: Only keep transitions where the entity owner name matches across sale and rental events (or both are null, indicating same individual owner)
5. **Deduplicate**: Keep earliest transition per property across all analysis dates

### Exclusion Criteria Applied
- Properties with completed sale transactions in the 110-day window (not implemented in this session; would require pulling SOLD events and filtering)
- Properties with multiple ownership changes (partially captured by same-owner check)

### Outlier Filtering
- Rents below $500/mo or above $10,000/mo removed
- Sale prices below $50,000 removed
- Gross yield below 2% or above 18% removed (catches bad data like $37K/mo rent on a $45K property)
- **62 records removed**, leaving 1,464 clean leads

## Key Results

| Metric | Value |
|--------|-------|
| Total qualified leads | 1,464 |
| Median list price | $324,945 |
| Median rent | $2,300/mo |
| Median gross yield | 8.5% |
| Mean gross yield | 8.6% |
| Top city | Houston (574 leads) |
| Top ZIP | 77433 (46 leads) |

## Dashboard Output

Single-file HTML dashboard with:
- Summary tab with KPI cards, bar charts, methodology
- Accidental Landlord tab with KPI strip, pitch angle insight box, ZIP/city distribution charts, searchable/filterable lead table (sorted by gross yield), methodology section
- Color palette: Genstone Property Management inspired (blue #2871CC, orange #E8841A, dark green #1A2E1F)
- All data embedded in the HTML, no external dependencies
