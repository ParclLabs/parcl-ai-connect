# Changelog

All notable changes to the Property Manager Intel skill are tracked in
this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-04-24

### Added

- Initial release of the Property Manager Intel skill.
- Four-tab xlsx output: PM Profiles (third-party PMs), Brokerages,
  Institutional Landlords, Rental Software & Platforms.
- Seven-tier PM resolution waterfall (`scripts/resolve_pm.py`) with
  primary routing via `company_type` and overlay fallback via curated
  reference lists.
- Curated reference lists in `scripts/lib/blocklists.py`:
  `RENTAL_SOFTWARE`, `BROKERAGES`, and `INSTITUTIONAL_LANDLORDS` with
  canonical-name collapsing for institutional operators.
- PM name normalization and dedup pipeline
  (`scripts/dedup_pm.py`, `scripts/build_profiles.py`,
  `scripts/build_spreadsheet.py`).
- Skill supports both market-scoped (MSA, city, ZIP) and national pulls
  from the `motivated_renter_properties` MCP tool.
- Reference documentation under `references/known_entities.md`.
