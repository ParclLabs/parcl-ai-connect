#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pandas>=2.0",
# ]
# ///
"""Step 3: consolidate PM name variants into canonical display names.

Input:  resolve_pm.py output (CSV with pm_entity_raw, pm_category, pm_is_filtered).
Output: same CSV with added columns:
    - pm_normalized      : lowercased canonical key (grouping key)
    - pm_display_name    : human-readable display name (institutional canonical
                           or most-frequent raw variant within each group)

Process:
    1. Drop filtered rows (pm_is_filtered == True) — rental software and
       unresolvable rows don't contribute to the final list.
    2. For each remaining row, compute the grouping key:
       - If the PM name matches a known institutional landlord, use the
         canonical institutional name as the display override + grouping key
         (so all institutional variants collapse together).
       - Otherwise, use normalize_pm_name(pm_entity_raw) as the grouping key.
    3. Group by pm_normalized. Within each group, pick the display name:
       - If an institutional override fired: use the canonical institutional name.
       - Otherwise: most-frequent raw variant wins (tie → longer name).

CLI:
    python dedup_pm.py --input RESOLVED.csv --output DEDUPED.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from lib.blocklists import match_institutional_landlord  # noqa: E402
from lib.normalize import normalize_pm_name, pick_display_name  # noqa: E402


def _resolve_canonical(raw_name: str) -> tuple[str, str]:
    """Resolve (display_override, normalized_key) for a single raw PM name.

    Returns:
        display_override: the institutional canonical name if the PM matches
            a known institutional landlord, otherwise "".
        normalized_key: the grouping key. If an institutional override fired,
            the key is the normalized form of the canonical institutional name
            (so all variants collapse). Otherwise the key is
            normalize_pm_name(raw_name).
    """
    if not raw_name:
        return "", ""

    # Institutional landlords — all variants collapse to the canonical.
    inst = match_institutional_landlord(normalize_pm_name(raw_name))
    if inst:
        return inst, normalize_pm_name(inst)

    # Normal path — no override, use the raw name's normalized form as the key.
    return "", normalize_pm_name(raw_name)


def dedup_pm_names(df: pd.DataFrame) -> pd.DataFrame:
    """Add pm_normalized and pm_display_name columns.

    Filtered rows (pm_is_filtered=True) are dropped first.
    """
    if "pm_is_filtered" in df.columns:
        df = df[~df["pm_is_filtered"]].copy()
    else:
        df = df.copy()

    if len(df) == 0:
        df["pm_normalized"] = []
        df["pm_display_name"] = []
        return df

    # Compute per-row overrides and normalization keys.
    overrides: list[str] = []
    keys: list[str] = []
    for raw in df["pm_entity_raw"].fillna("").astype(str):
        ov, k = _resolve_canonical(raw)
        overrides.append(ov)
        keys.append(k)

    df["_display_override"] = overrides
    df["pm_normalized"] = keys

    # Drop rows that normalize to empty (shouldn't happen after filtering but
    # defensive — protects downstream groupby from empty-string PMs).
    df = df[df["pm_normalized"] != ""].copy()

    # Resolve display name per group.
    display_map: dict[str, str] = {}
    for key, group in df.groupby("pm_normalized"):
        non_empty_overrides = [o for o in group["_display_override"] if o]
        if non_empty_overrides:
            display_map[key] = pick_display_name(non_empty_overrides)
        else:
            display_map[key] = pick_display_name(group["pm_entity_raw"].tolist())

    df["pm_display_name"] = df["pm_normalized"].map(display_map)
    df = df.drop(columns=["_display_override"])
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True, help="resolve_pm output CSV")
    ap.add_argument("--output", required=True, help="deduped output CSV")
    args = ap.parse_args()

    df = pd.read_csv(args.input, low_memory=False)
    before = len(df)
    deduped = dedup_pm_names(df)
    after = len(deduped)
    groups = deduped["pm_normalized"].nunique()

    deduped.to_csv(args.output, index=False)
    print(f"dedup_pm: rows_in={before} rows_out={after} unique_pms={groups}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
