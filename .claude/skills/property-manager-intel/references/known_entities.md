# Known Entities

This doc describes the three curated reference lists in
`scripts/lib/blocklists.py`.

The lists function as an overlay on top of the `company_type` column.
`company_type` is the authoritative classification; the overlay lists
apply only when `company_type` is NaN or `other`.

## RENTAL_SOFTWARE

Listing platforms and PM software. Matches route to the Rental Software
& Platforms tab — kept visible as a leasing-activity surface but not
ranked alongside PMs.

Examples: Zumper, AppFolio, Buildium, Propertyware, TurboTenant,
ShowMojo, TenantTurner.

## BROKERAGES

Real-estate brokerages. Listings attributed to these go on the Brokerages
tab, not the main PM Profiles tab.

Includes major national brands (Keller Williams, RE/MAX, Coldwell Banker,
Compass, Century 21, eXp, Sotheby's, Berkshire Hathaway, Douglas Elliman,
Corcoran, etc.) and regional / market-specific brands (West USA Realty,
Russ Lyon, Launch, Fathom, Ranch Realty, LPT Realty, The Keyes Company,
Real Broker, Lokation, HomeSmart, Long Realty, Realty One Group, etc.).

**How to add an entry:** lowercased substring match. "keller williams"
catches "Keller Williams Realty Phoenix" and similar variants.
**Gotcha:** don't add a version that includes filler words the normalizer
strips — add the root brand fragment. Also avoid very short entries
(≤ 4 characters) that could substring-match innocent words (e.g. "side"
would match "residential").

## INSTITUTIONAL_LANDLORDS

Named SFR investor-operators that manage their own portfolios. The dict
maps canonical display names → a tuple of alias substrings checked against
the normalized PM name.

Covered entities include:
- American Homes 4 Rent (AMH)
- Tricon Residential
- Invitation Homes
- Home Partners of America
- Progress Residential
- FirstKey Homes
- Amherst Holdings
- VineBrook Homes
- Maymont Homes
- SFR3
- My Community Homes
- Blackstone
- Opendoor
- Offerpad
- Main Street Renewal (branded independently from Amherst, kept as a
  separate canonical)
- Pathway Homes, Divvy Homes

**How to add an entry:**

```python
INSTITUTIONAL_LANDLORDS["Canonical Display Name"] = (
    "alias one",
    "alternative spelling",
    "abbreviation",
)
```

Aliases must be lowercased. They're matched as substrings against the
normalized input, so short aliases ("amh") work but may have false
positives — the test suite's overlap tests catch the common ones.

## Overlap rules

The test suite enforces no overlap between:
- `RENTAL_SOFTWARE` ∩ `BROKERAGES` must be empty
- `RENTAL_SOFTWARE` ∩ institutional aliases must be empty
- `BROKERAGES` ∩ institutional aliases must be empty

If a new entry would overlap, decide which list it belongs in and leave
the other alone.
