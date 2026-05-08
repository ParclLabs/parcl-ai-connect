"""Name normalization for property manager entity consolidation.

The goal is to collapse "Main Street Renewal", "Main Street Renewal LLC",
"Main Street Renewal, Llc" — and similar variants — to a single canonical
key so we can count them as one PM.

Strategy:
  1. Lowercase, strip outer whitespace.
  2. Strip common legal suffixes (LLC, Inc, Corp, Ltd, LP, etc).
  3. Strip generic functional words (Group, Services, Solutions, etc) that
     get appended and subtracted willy-nilly in the real world.
  4. Remove punctuation, collapse whitespace, strip residual edges.

The result is the *normalized key* — used for grouping, not for display.
The display name is picked separately (most-frequent raw variant wins).
"""

from __future__ import annotations

import re


# Legal-form suffixes. Two alternations:
#   1. Dotted forms (L.L.C., L.P., etc.) — matched literally. Cannot use a
#      trailing \b because "." is non-word and \b won't fire there.
#   2. Plain forms (LLC, Inc, Corp, etc.) — matched as whole words with an
#      optional trailing period.
_LEGAL_SUFFIXES = re.compile(
    r"\b(?:l\.l\.c\.|l\.p\.|l\.l\.p\.|p\.c\.|p\.a\.)"
    r"|"
    r"\b(?:llc|inc|incorporated|corp|corporation|co|company|"
    r"ltd|limited|lp|llp|lc|pllc|pc|pa)\b\.?",
    flags=re.IGNORECASE,
)

# Anything not alphanumeric / whitespace / hyphen.
_PUNCT = re.compile(r"[^\w\s\-]")

# Collapse whitespace runs.
_WS = re.compile(r"\s+")


def normalize_pm_name(name: object) -> str:
    """Return a normalized key for a PM name.

    Strips legal suffixes (LLC / Inc / Corp / etc.), punctuation, and
    collapses whitespace. Does NOT strip content words like "Group" /
    "Partners" / "Holdings" / "Services" / "Homes" / "Realty" — stripping
    those caused false-positive substring matches (e.g., the alias
    "home partners" collapsing to "home" and matching every company with
    "home" in the name).

    Variant consolidation for content-word differences is handled instead by
    the curated alias sets in blocklists.py (INSTITUTIONAL_LANDLORDS).

    Returns:
        Normalized key (lowercased, stripped, collapsed). Empty string if
        the input is None/NaN/empty/whitespace.
    """
    if name is None:
        return ""
    s = str(name).strip()
    if not s or s.lower() in ("nan", "none", "null"):
        return ""

    s = s.lower()
    s = _LEGAL_SUFFIXES.sub(" ", s)
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    s = s.strip("-").strip()
    return s


def pick_display_name(raw_names: list[str]) -> str:
    """Pick the most-frequent raw name as the display name.

    Ties broken by (longer is better, then alphabetical) — longer usually
    preserves more of the real branding ("Main Street Renewal" over "MSR").
    """
    if not raw_names:
        return ""
    # Count occurrences.
    counts: dict[str, int] = {}
    for n in raw_names:
        if n is None:
            continue
        s = str(n).strip()
        if not s:
            continue
        counts[s] = counts.get(s, 0) + 1
    if not counts:
        return ""
    # Sort: highest count first, then longest string, then alphabetical.
    best = sorted(counts.items(), key=lambda kv: (-kv[1], -len(kv[0]), kv[0]))[0]
    return best[0]
