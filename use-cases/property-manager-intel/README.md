# Property Manager Intel

Build a ranked list of rental property managers with portfolio scale, geography, and contact info — cleanly separated so you never confuse a third-party PM with a brokerage or an institutional landlord.

![Property Manager Intel Demo](../../assets/gifs/pm_intelligence_small.gif)

## What You Get

A four-tab Excel workbook plus a summary sheet:

- **PM Profiles** — third-party property managers (and corporate-housing operators like Blueground and Nomad Homes), ranked by active rentals. The main prospecting list.
- **Brokerages** — Keller Williams, RE/MAX, Compass, and similar. Their agents list rentals, but the brokerage is not a PM contract — kept visible as a leasing-activity surface.
- **Institutional Landlords** — Invitation Homes, AMH, Progress Residential, FirstKey, Tricon, and similar SFR operators that manage their own portfolios. Name variants collapse to one canonical display.
- **Rental Software & Platforms** — Zumper, AppFolio, Zillow, ShowMojo, and similar. Platforms facilitating listings, not PMs.

Each PM row includes: active rentals, states, top MSAs, cities, ZIPs, rent/sqft/DOM stats, property-type mix, motivated-renter index, algo-pricing share, representative email and phone, and a resolution-source audit trail.

## Choose Your Path

### Basic (Copy & Paste)

No setup required. Copy the prompt from [`basic/PROMPT.md`](basic/PROMPT.md) into Claude Code with the Parcl Labs MCP connected.

### Advanced (Skill)

Run `/property-manager-intel [market name or 'national']` in Claude Code for a fully automated pipeline with:

- Seven-tier PM resolution waterfall that handles classified `company_type` rows, platform-masked PMs (agent-behind-platform), and the unflagged long tail
- Curated overlay lists for brokerages, institutional operators, and listing platforms with canonical-name collapsing
- Four-tab xlsx output with frozen headers, autofilters, and a summary sheet

See the [skill definition](../../.claude/skills/property-manager-intel/SKILL.md) and the [changelog](../../.claude/skills/property-manager-intel/CHANGELOG.md) for details.

## Key Concepts

- **`company_type` is authoritative.** Parcl's classification (`property_management`, `brokerage`, `institutional_landlord`, `corporate_housing`, `rental_software_platform`, `listing_platform`, `homebuilder`, `other`) drives the primary routing. Overlay lists only run when `company_type` is NaN or `other`.
- **Institutional `active_rentals` reflects listings, not doors managed.** A large SFR operator may own tens of thousands of homes with only a fraction actively listed at any moment.
- **Per-PM geography is based on active listings.** `num_states` / `num_msas` / `num_cities` / `num_zips` count where a PM currently has rentals listed — a lower bound on where they operate.
- **Contact-fill rates vary by source.** `representative_email` and `representative_phone` populate at roughly 40–60% on third-party PMs and near-zero on institutional operators.
