#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.0",
#     "numpy>=1.24",
# ]
# ///
"""Step 4: aggregate per-property rows into PM-level profiles.

Input:  dedup_pm.py output (CSV with pm_display_name, pm_normalized, pm_category).
Output: profiles CSV with one row per PM, sorted by active_rentals desc.

For each PM we compute:
    - active_rentals        : count of properties
    - num_states, states    : unique state count + sorted comma list
    - num_msas, top_msas    : unique MSA count + top-5 by frequency
    - num_cities, num_zips  : unique city / zip counts
    - avg_rent, median_rent : central tendency on latest_listing_rent
    - avg_sqft              : average square footage
    - avg_dom, median_dom   : days-on-market stats
    - pct_single_family     : share of SFR
    - pct_condo             : share of condos
    - pct_townhouse         : share of townhouses
    - avg_mri               : mean motivated-renter-index value
    - pct_desperate_to_lease, pct_motivated : motivated-renter-index label distribution
    - pct_algo_pricing      : share flagged for algorithmic pricing
    - primary_company_type  : mode of company_type column
    - is_pm_flagged         : any row with is_property_management_company=1
    - category              : third_party | brokerage | institutional_landlord |
                              rental_software (taken from pm_category;
                              institutional wins ties)
    - contact_fill_rate     : fraction of rows with non-empty email or phone
    - top_resolution_source : mode of pm_resolution_source (audit trail)

Arrays of names (states, top_msas) are joined with ", " for CSV-friendliness.

CLI:
    python build_profiles.py --input DEDUPED.csv --output PROFILES.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _top_n_joined(series: pd.Series, n: int = 5) -> str:
    """Top-N most frequent non-null values, joined with ', '."""
    s = series.dropna().astype(str)
    s = s[s != ""]
    if len(s) == 0:
        return ""
    return ", ".join(s.value_counts().head(n).index)


def _pick_category(categories: pd.Series) -> str:
    """Pick a single category label per PM by majority vote.

    A PM whose per-row category tags are mixed (e.g. 123 rows tagged
    property_management and 1 row tagged institutional_landlord) should
    be assigned by majority, not by strict precedence.

    Tie-breaker ordering when counts are equal: institutional > brokerage
    > third_party > rental_software. Institutional keeps priority on ties
    because it's a strong identity signal when genuinely present.
    """
    s = list(categories.dropna())
    if not s:
        return "unknown"
    counts: dict[str, int] = {}
    for c in s:
        counts[c] = counts.get(c, 0) + 1
    best = max(counts.values())
    for preferred in ("institutional_landlord", "brokerage", "third_party", "rental_software"):
        if counts.get(preferred, 0) == best:
            return preferred
    # No known category matched — pick whichever category has the most rows.
    return max(counts, key=counts.get)


def _mode_or_empty(series: pd.Series) -> str:
    s = series.dropna().astype(str)
    s = s[s != ""]
    if len(s) == 0:
        return ""
    return s.mode().iat[0]


# Known syndication-relay / automation addresses that carry no outreach
# value — populated on many rows but route to a relay inbox, not the real
# listing agent. When picking a representative email we deprioritize
# these: we'd rather surface a legitimate agent address. If ALL emails on
# a PM are relays, we fall back to the most-frequent one (better than
# leaving the column blank).
_EMAIL_RELAY_SUBSTRINGS = (
    "rentalbeast.com",          # realtor.com_leads@rentalbeast.com etc.
    "@move.com",                # rentalservice@move.com
    "showmojo.com",             # *+syndication+*@email1.showmojo.com
    "+syndication+",            # generic syndication-relay pattern
    "noreply@",
    "no-reply@",
    "donotreply@",
    "do-not-reply@",
    "notifications@",
)


def _is_relay_email(s: str) -> bool:
    s = s.lower()
    return any(token in s for token in _EMAIL_RELAY_SUBSTRINGS)


def _contact_fill_rate(group: pd.DataFrame) -> float:
    """Fraction of rows with non-empty email OR phone."""
    email_cols = [c for c in ("agent_email",) if c in group.columns]
    phone_cols = [c for c in ("agent_phone",) if c in group.columns]

    has_contact = pd.Series(False, index=group.index)
    for col in email_cols + phone_cols:
        vals = group[col].fillna("").astype(str).str.strip()
        has_contact = has_contact | ((vals != "") & (vals.str.lower() != "nan"))
    if len(group) == 0:
        return 0.0
    return float(has_contact.mean())


def _sample_contact(group: pd.DataFrame) -> tuple[str, str]:
    """Return (representative_email, representative_phone).

    For email: pick the most-frequent legitimate (non-relay) address.
    If none, fall back to the most-frequent address overall (including
    relays) — better to surface something than leave the column blank.
    For phone: most-frequent non-empty.
    """
    email = ""
    phone = ""

    if "agent_email" in group.columns:
        vals = group["agent_email"].fillna("").astype(str)
        vals = vals[(vals != "") & (vals.str.lower() != "nan")]
        if len(vals):
            # Prefer legitimate addresses.
            legit = vals[~vals.map(_is_relay_email)]
            if len(legit):
                email = legit.value_counts().index[0]
            else:
                # Fall back to most-frequent overall.
                email = vals.value_counts().index[0]

    if "agent_phone" in group.columns:
        vals = group["agent_phone"].fillna("").astype(str)
        vals = vals[(vals != "") & (vals.str.lower() != "nan")]
        if len(vals):
            phone = vals.value_counts().index[0]

    return email, phone


def build_profile(group: pd.DataFrame) -> dict:
    """Compute the profile row for one PM group."""
    n = len(group)

    def _pct(series: pd.Series, value: str, case_sensitive: bool = True) -> float:
        s = series.dropna().astype(str)
        if not case_sensitive:
            s = s.str.lower()
            value = value.lower()
        return float((s == value).mean()) if len(s) else 0.0

    def _pct_truthy(series: pd.Series) -> float:
        if len(series) == 0:
            return 0.0
        # treat 1/1.0/True/"1"/"true" as True
        def t(v):
            if v is None:
                return False
            try:
                if pd.isna(v):
                    return False
            except (TypeError, ValueError):
                pass
            if isinstance(v, bool):
                return v
            if isinstance(v, (int, float)):
                return v != 0
            return str(v).strip().lower() in ("1", "1.0", "true", "yes", "y", "t")

        return float(np.mean([t(v) for v in series]))

    states = sorted(set(group["state"].dropna().astype(str))) if "state" in group else []
    msas = group["msa_name"] if "msa_name" in group else pd.Series([], dtype=object)
    cities = group["city"] if "city" in group else pd.Series([], dtype=object)
    zips = group["zip5"] if "zip5" in group else pd.Series([], dtype=object)

    email, phone = _sample_contact(group)

    return {
        "pm_display_name": group["pm_display_name"].iloc[0],
        "pm_normalized": group["pm_normalized"].iloc[0],
        "category": _pick_category(group["pm_category"]),
        "active_rentals": n,
        "num_states": len(states),
        "states": ", ".join(states),
        "num_msas": msas.nunique(),
        "top_msas": _top_n_joined(msas, 5),
        "num_cities": cities.nunique(),
        "num_zips": zips.astype(str).replace("nan", "").replace("", np.nan).dropna().nunique(),
        "avg_rent": round(float(group["latest_listing_rent"].dropna().mean()), 2) if "latest_listing_rent" in group and group["latest_listing_rent"].notna().any() else None,
        "median_rent": round(float(group["latest_listing_rent"].dropna().median()), 2) if "latest_listing_rent" in group and group["latest_listing_rent"].notna().any() else None,
        "avg_sqft": round(float(group["sq_ft"].dropna().mean()), 0) if "sq_ft" in group and group["sq_ft"].notna().any() else None,
        "avg_dom": round(float(group["days_on_market"].dropna().mean()), 1) if "days_on_market" in group and group["days_on_market"].notna().any() else None,
        "median_dom": round(float(group["days_on_market"].dropna().median()), 1) if "days_on_market" in group and group["days_on_market"].notna().any() else None,
        "pct_single_family": round(_pct(group.get("property_type", pd.Series(dtype=object)), "SINGLE_FAMILY") * 100, 1),
        "pct_condo": round(_pct(group.get("property_type", pd.Series(dtype=object)), "CONDO") * 100, 1),
        "pct_townhouse": round(_pct(group.get("property_type", pd.Series(dtype=object)), "TOWNHOUSE") * 100, 1),
        "avg_mri": round(float(group["motivated_renter_index_value"].dropna().mean()), 2) if "motivated_renter_index_value" in group and group["motivated_renter_index_value"].notna().any() else None,
        "pct_desperate_to_lease": round(_pct(group.get("motivated_renter_index_label", pd.Series(dtype=object)), "desperate_to_lease") * 100, 1),
        "pct_motivated": round(_pct(group.get("motivated_renter_index_label", pd.Series(dtype=object)), "motivated") * 100, 1),
        "pct_algo_pricing": round(_pct_truthy(group.get("algorithmic_pricing_detected", pd.Series(dtype=object))) * 100, 1),
        "primary_company_type": _mode_or_empty(group.get("company_type", pd.Series(dtype=object))),
        "is_pm_flagged": bool(_pct_truthy(group.get("is_property_management_company", pd.Series(dtype=object))) > 0),
        "contact_fill_rate": round(_contact_fill_rate(group) * 100, 1),
        "representative_email": email,
        "representative_phone": phone,
        "top_resolution_source": _mode_or_empty(group.get("pm_resolution_source", pd.Series(dtype=object))),
    }


def build_profiles(df: pd.DataFrame) -> pd.DataFrame:
    """Group by pm_normalized and compute profile rows."""
    if len(df) == 0:
        return pd.DataFrame()

    rows = []
    for _, group in df.groupby("pm_normalized"):
        rows.append(build_profile(group))

    profiles = pd.DataFrame(rows)
    # Sort: category first (institutional / brokerage stay visible but after
    # third_party for ranking purposes; the spreadsheet separates them by tab
    # anyway), then active_rentals desc.
    profiles = profiles.sort_values("active_rentals", ascending=False, kind="stable")
    return profiles.reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True, help="dedup_pm output CSV")
    ap.add_argument("--output", required=True, help="profiles CSV")
    args = ap.parse_args()

    df = pd.read_csv(args.input, low_memory=False)
    profiles = build_profiles(df)
    profiles.to_csv(args.output, index=False)

    total = len(profiles)
    third = int((profiles["category"] == "third_party").sum())
    brok = int((profiles["category"] == "brokerage").sum())
    inst = int((profiles["category"] == "institutional_landlord").sum())
    soft = int((profiles["category"] == "rental_software").sum())
    print(
        f"build_profiles: pms={total} third_party={third} "
        f"brokerage={brok} institutional={inst} rental_software={soft}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
