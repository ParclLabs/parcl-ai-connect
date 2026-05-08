#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.0",
# ]
# ///
"""Step 2: assign a PM name and category to each rental listing.

Input:  CSV of raw rental listings from `motivated_renter_properties`.
Output: same CSV with four new columns:
    - pm_entity_raw         : the resolved PM name (None if unresolvable)
    - pm_resolution_source  : which tier of the waterfall matched
    - pm_category           : third_party | brokerage | institutional_landlord |
                              rental_software | unresolved
    - pm_is_filtered        : True if this row should be DROPPED from the final
                              list. Covers both (a) rows with no resolvable PM
                              candidate and (b) policy-filtered company types
                              (currently `homebuilder` via _PARCL_FILTER_OUT,
                              which is routed to Category.UNRESOLVED — no PM
                              signal to surface).

RESOLUTION WATERFALL — picks the best PM-name candidate per row. First match wins:

    1. company_name when company_type is property_management or
       institutional_landlord.
    2. property_manager (when not a known software/listing-platform override).
    3. company_name (when not software).
    4. agent_business when is_property_management_company == 1 (not software).
    5. agent_business when property_manager is a known software/listing-platform
       override (the agent_business is the real PM hiding behind the platform).
    6. agent_business (any flag, not software) — the coverage-expansion tier
       that catches PMs missing from earlier tiers.
    7. Last-resort: any populated candidate — even a software name — so
       categorize() can still route the listing to the Rental Software tab
       (software names don't get dropped silently, they get segmented).

CATEGORIZATION — `company_type` is the primary signal. The overlay lists in
lib/blocklists.py apply only when `company_type` is NaN or `other`.

company_type → category:
    institutional_landlord    → institutional_landlord tab
    brokerage                 → brokerage tab
    property_management       → third_party tab
    corporate_housing         → third_party tab (Blueground, Nomad Homes, etc.)
    rental_software_platform  → rental_software tab
    listing_platform          → rental_software tab
    homebuilder               → filtered out (no PM signal)
    other / NaN               → fall through to overlay fallback

Fallback (when company_type is NaN / other):
    1. entity_name / parent_company matches institutional alias → institutional tab
    2. resolved PM name matches institutional alias → institutional tab
    3. resolved PM name matches rental-software overlay → rental_software tab
    4. resolved PM name matches brokerage overlay → brokerage tab
    5. default → third_party tab

INSTITUTIONAL CANONICAL NAMING: whenever a listing routes to the institutional
tab (via Parcl company_type or entity-level override), the display name is
resolved to its canonical form via INSTITUTIONAL_LANDLORDS — so "First Key Homes"
/ "FirstKey" / "FKH" all collapse to one canonical display name.

CLI:
    python resolve_pm.py --input LISTINGS.csv --output RESOLVED.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Make lib importable when this script is run directly.
sys.path.insert(0, str(Path(__file__).parent))

from lib.blocklists import (  # noqa: E402
    is_brokerage,
    is_rental_software,
    match_institutional_landlord,
)
from lib.normalize import normalize_pm_name  # noqa: E402


# Resolution source labels. Keep these stable — downstream reports key on them.
class Source:
    COMPANY_CLASSIFIED = "company_name_classified"
    PROPERTY_MANAGER_DIRECT = "property_manager_direct"
    COMPANY_FALLBACK = "company_name_fallback"
    AGENT_PM_FLAGGED = "agent_business_pm_flagged"
    AGENT_BEHIND_PLATFORM = "agent_business_behind_platform"
    AGENT_EXPANDED = "agent_business_expanded"
    UNRESOLVED = "unresolved"


# Category labels. Stable — downstream tabs key on these.
class Category:
    THIRD_PARTY = "third_party"
    BROKERAGE = "brokerage"
    INSTITUTIONAL = "institutional_landlord"
    RENTAL_SOFTWARE = "rental_software"
    UNRESOLVED = "unresolved"


# company_type values that indicate a real PM/landlord (tier 2 of the waterfall).
_PM_COMPANY_TYPES = {"property_management", "institutional_landlord"}


def _clean_str(val: Any) -> str:
    """Return a stripped string or '' for None/NaN/empty/'nan'/'None'."""
    if val is None:
        return ""
    try:
        if pd.isna(val):
            return ""
    except (TypeError, ValueError):
        pass
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "null"):
        return ""
    return s


def resolve_row(row: dict) -> tuple[str, str]:
    """Run the 7-tier waterfall and return (pm_name, source).

    Returns ("", Source.UNRESOLVED) if nothing matches.
    """
    pm = _clean_str(row.get("property_manager"))
    cn = _clean_str(row.get("company_name"))
    ab = _clean_str(row.get("agent_business"))
    ct = _clean_str(row.get("company_type")).lower()
    is_pm_flag = row.get("is_property_management_company")

    pm_norm = normalize_pm_name(pm)
    cn_norm = normalize_pm_name(cn)
    ab_norm = normalize_pm_name(ab)

    # Tier 1: classified company_name.
    if cn and ct in _PM_COMPANY_TYPES and not is_rental_software(cn_norm):
        return cn, Source.COMPANY_CLASSIFIED

    # Tier 2: property_manager direct (if not software).
    if pm and not is_rental_software(pm_norm):
        return pm, Source.PROPERTY_MANAGER_DIRECT

    # Tier 3: company_name fallback (any company_type).
    if cn and not is_rental_software(cn_norm):
        return cn, Source.COMPANY_FALLBACK

    # Tier 4: agent_business when is_pm flag is set.
    if ab and _truthy(is_pm_flag) and not is_rental_software(ab_norm):
        return ab, Source.AGENT_PM_FLAGGED

    # Tier 5: agent_business behind a software platform.
    if ab and pm and is_rental_software(pm_norm) and ab_norm != pm_norm and not is_rental_software(ab_norm):
        return ab, Source.AGENT_BEHIND_PLATFORM

    # Tier 6: agent_business expanded (no PM flag required).
    if ab and not is_rental_software(ab_norm):
        return ab, Source.AGENT_EXPANDED

    # Tier 7: last-resort software name. If every candidate above was either
    # empty or software, return the first populated one so categorize() can
    # route the listing to the Rental Software tab (software listings don't
    # get dropped silently — they get segmented).
    for val, label in (
        (pm, Source.PROPERTY_MANAGER_DIRECT),
        (cn, Source.COMPANY_FALLBACK),
        (ab, Source.AGENT_EXPANDED),
    ):
        if val:
            return val, label

    return "", Source.UNRESOLVED


def _truthy(val: Any) -> bool:
    """Handle 1 / 1.0 / True / "1" / "true" as True; 0 / NaN / None / "" as False."""
    if val is None:
        return False
    try:
        if pd.isna(val):
            return False
    except (TypeError, ValueError):
        pass
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    s = str(val).strip().lower()
    return s in ("1", "1.0", "true", "yes", "y", "t")


def _institutional_canonical_name(pm_name: str, row: dict | None) -> str:
    """Try to resolve a canonical institutional display name.

    Checks the resolved pm_name first, then entity_name and parent_company
    (which often carry the institutional brand even when the listing's PM
    fields do not). Falls back to the raw pm_name if no canonical match.
    """
    hit = match_institutional_landlord(normalize_pm_name(pm_name))
    if hit:
        return hit
    if row is not None:
        for field in ("entity_name", "parent_company"):
            v = _clean_str(row.get(field))
            if v:
                hit = match_institutional_landlord(normalize_pm_name(v))
                if hit:
                    return hit
    return pm_name


# company_type values and where they route.
_PARCL_INSTITUTIONAL = "institutional_landlord"
_PARCL_BROKERAGE = "brokerage"
_PARCL_PROPERTY_MANAGEMENT = "property_management"
_PARCL_CORPORATE_HOUSING = "corporate_housing"
_PARCL_SOFTWARE_TYPES = {"rental_software_platform", "listing_platform"}
_PARCL_FILTER_OUT = {"homebuilder"}
# company_type values that fall through to the overlay fallback.
# (Empty string = NaN; "other" is the low-signal class.)
_PARCL_FALLBACK = {"", "other"}


def categorize(
    pm_name: str,
    row: dict | None = None,
) -> tuple[str, str]:
    """Return (final_pm_name, category) for a resolved PM name.

    `company_type` is the primary signal. The overlay lists apply only
    when `company_type` is NaN or `other`.

    If `row` is None (unit tests), the function runs the overlay fallback
    path, equivalent to company_type=NaN.
    """
    if not pm_name:
        return "", Category.UNRESOLVED

    ct = _clean_str(row.get("company_type")).lower() if row is not None else ""

    # Primary: Parcl's company_type.
    if ct == _PARCL_INSTITUTIONAL:
        return _institutional_canonical_name(pm_name, row), Category.INSTITUTIONAL
    if ct == _PARCL_BROKERAGE:
        return pm_name, Category.BROKERAGE
    if ct == _PARCL_PROPERTY_MANAGEMENT:
        return pm_name, Category.THIRD_PARTY
    if ct == _PARCL_CORPORATE_HOUSING:
        return pm_name, Category.THIRD_PARTY
    if ct in _PARCL_SOFTWARE_TYPES:
        return pm_name, Category.RENTAL_SOFTWARE
    if ct in _PARCL_FILTER_OUT:
        return pm_name, Category.UNRESOLVED

    # Fallback: company_type is NaN / other. Use overlay lists and
    # entity-level signals to route.

    # Entity-level institutional override: if entity_name or parent_company
    # matches an institutional landlord, route there.
    if row is not None:
        for field in ("entity_name", "parent_company"):
            v = _clean_str(row.get(field))
            if v:
                hit = match_institutional_landlord(normalize_pm_name(v))
                if hit:
                    return hit, Category.INSTITUTIONAL

    pm_norm = normalize_pm_name(pm_name)

    # Check institutional via the resolved PM name itself.
    inst = match_institutional_landlord(pm_norm)
    if inst:
        return inst, Category.INSTITUTIONAL

    # Software / platform override — routes to rental_software tab.
    if is_rental_software(pm_norm):
        return pm_name, Category.RENTAL_SOFTWARE

    # Brokerage override.
    if is_brokerage(pm_norm):
        return pm_name, Category.BROKERAGE

    # Default: third-party PM.
    return pm_name, Category.THIRD_PARTY


def resolve_listings(df: pd.DataFrame) -> pd.DataFrame:
    """Top-level resolver: run the waterfall row-by-row."""
    # Run row-level resolution. Iterate rows as dicts to keep memory reasonable
    # at scale — this avoids copying the whole frame for .apply.
    records = df.to_dict("records")
    names: list[str] = []
    sources: list[str] = []
    categories: list[str] = []
    filtered: list[bool] = []
    final_names: list[str] = []

    for row in records:
        pm, src = resolve_row(row)
        final_name, category = categorize(pm, row)
        names.append(pm)
        sources.append(src)
        categories.append(category)
        final_names.append(final_name)
        filtered.append(category == Category.UNRESOLVED)

    df = df.copy()
    df["pm_entity_raw"] = final_names  # post-institutional-override name
    df["pm_resolution_source"] = sources
    df["pm_category"] = categories
    df["pm_is_filtered"] = filtered

    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True, help="input listings CSV")
    ap.add_argument("--output", required=True, help="output resolved CSV")
    args = ap.parse_args()

    df = pd.read_csv(args.input, low_memory=False)

    resolved = resolve_listings(df)
    resolved.to_csv(args.output, index=False)

    total = len(resolved)
    kept = int((~resolved["pm_is_filtered"]).sum())
    inst = int((resolved["pm_category"] == Category.INSTITUTIONAL).sum())
    brok = int((resolved["pm_category"] == Category.BROKERAGE).sum())
    third = int((resolved["pm_category"] == Category.THIRD_PARTY).sum())
    soft = int((resolved["pm_category"] == Category.RENTAL_SOFTWARE).sum())
    unres = int((resolved["pm_category"] == Category.UNRESOLVED).sum())

    print(
        f"resolve_pm: total={total} kept={kept} "
        f"third_party={third} brokerage={brok} institutional={inst} "
        f"rental_software={soft} unresolved={unres}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
