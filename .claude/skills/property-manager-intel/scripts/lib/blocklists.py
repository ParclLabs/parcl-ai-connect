"""Curated industry reference data for PM categorization.

Three overlay lists supplement the `company_type` column when it is
NaN or `other`, routing rows to the correct tab and consolidating
variant spellings into canonical display names. See
references/known_entities.md for the lists and curation notes.
"""

from __future__ import annotations

from .normalize import normalize_pm_name

RENTAL_SOFTWARE: set[str] = {
    "appfolio",
    "appfoliounits",
    "showmojo",
    "show mojo",
    "zumper",
    "rentengine",
    "rent engine",
    "tenantturner",
    "tenant turner",
    "zillow",
    "gmail",
    "yahoo",
    "hotmail",
    "outlook.com",
    "outlook com",
    "aol.com",
    "aol com",
    "icloud",
    "cloudmailin",
    "regionalmls",
    "mlsnow",
    "mls now",
    "mlsmatrix",
    "arizonaregionalmls",
    "arizona regional mls",
    "stellarmls",
    "stellar mls",
    "mlslistings",
    "mls listings",
    "brightmls",
    "bright mls",
    "mris",
    "ntreis",
    "unlockmls",
    "unlock mls",
    "bloomington board of realtors",
    "doorifymls",
    "doorify mls",
}


# -----------------------------------------------------------------------------
# BROKERAGES: real-estate brokerages. Separate tab, never ranked as PMs.
# -----------------------------------------------------------------------------
# Matched as normalized substrings (e.g. "keller williams" matches
# "Keller Williams Realty Phoenix"). Avoid short substrings that would
# collide with innocent words.
BROKERAGES: set[str] = {
    "keller williams",
    "re/max",
    "remax",
    "re max",
    "coldwell banker",
    "century 21",
    "exit realty",
    "exit realty corp",
    "berkshire hathaway",
    "berkshire hathaway homeservices",
    "compass",
    "exp realty",
    "e x p realty",
    "exp world",
    "sotheby",
    "realty one group",
    "howard hanna",
    "long realty",
    "long and foster",
    "long foster",
    "weichert",
    "douglas elliman",
    "corcoran",
    "william raveis",
    "nexthome",
    "next home",
    "homesmart",
    "home smart",
    "united real estate",
    "realty executives",
    "better homes and gardens",
    "bhhs",
    "the real estate group",
    "my home group",
    "my home gp",
    "russ lyon",
    "russ lyon sotheby",
    "west usa realty",
    "hunt real estate",
    "fathom realty",
    "ranch realty",
    "launch powered by compass",
    "lpt realty",
    "the keyes company",
    "keyes company",
    "real broker",
    "lokation real estate",
    "lokation",
    "corcoran group",
    "the corcoran group",
    "redfin",
}


# -----------------------------------------------------------------------------
# INSTITUTIONAL_LANDLORDS: named SFR operators. Routes matches to the
# Institutional Landlords tab and collapses spelling variants to a single
# canonical display name.
# -----------------------------------------------------------------------------
# Keys are the canonical display name; values are alias substrings checked
# against the normalized PM name.
INSTITUTIONAL_LANDLORDS: dict[str, tuple[str, ...]] = {
    "American Homes 4 Rent": ("american homes 4 rent", "amh", "american homes for rent"),
    "Invitation Homes": ("invitation homes",),
    "Progress Residential": ("progress residential",),
    "FirstKey Homes": ("firstkey homes", "first key homes", "firstkey"),
    "Tricon Residential": ("tricon residential", "tricon american homes"),
    "Main Street Renewal": ("main street renewal", "msrenewal", "mainstreetrenewal"),
    "Amherst Holdings": ("amherst holdings", "amherst residential"),
    "VineBrook Homes": ("vinebrook homes", "vinebrook"),
    "Maymont Homes": ("maymont homes", "maymont"),
    "SFR3": ("sfr3",),
    "My Community Homes": ("my community homes", "mycommunityhomes"),
    "Blackstone": ("blackstone",),
    "Home Partners of America": ("home partners of america", "home partners"),
    "Opendoor": ("opendoor",),
    "Offerpad": ("offerpad",),
    "Pathway Homes": ("pathway homes",),
    "Divvy Homes": ("divvy homes", "divvy"),
}


# -----------------------------------------------------------------------------
# Pre-normalized matching sets
# -----------------------------------------------------------------------------
# The sets above are in human-readable form. The `is_*` helpers receive input
# that's already normalized. We pre-normalize the entries so both sides match
# consistently.
#
# Entries that normalize to empty are dropped (edge case — e.g. "holdings"
# alone would normalize to "") to prevent accidentally matching everything.

_RENTAL_SOFTWARE_NORMALIZED: frozenset[str] = frozenset(
    n for n in (normalize_pm_name(s) for s in RENTAL_SOFTWARE) if n
)
_BROKERAGES_NORMALIZED: frozenset[str] = frozenset(
    n for n in (normalize_pm_name(b) for b in BROKERAGES) if n
)
_INSTITUTIONAL_NORMALIZED: dict[str, tuple[str, ...]] = {
    canonical: tuple(n for n in (normalize_pm_name(a) for a in aliases) if n)
    for canonical, aliases in INSTITUTIONAL_LANDLORDS.items()
}


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def is_rental_software(normalized_name: str) -> bool:
    """True if the normalized name matches a rental-software override entry.

    Input must already be normalized via `normalize_pm_name` (legal suffixes
    stripped). Match is substring against the pre-normalized RENTAL_SOFTWARE
    set — so "listed via appfolio" matches "appfolio".
    """
    if not normalized_name:
        return False
    n = normalized_name.lower().strip()
    for software in _RENTAL_SOFTWARE_NORMALIZED:
        if software and software in n:
            return True
    return False


def is_brokerage(normalized_name: str) -> bool:
    """True if the normalized name matches a known brokerage (substring match).

    Input must already be normalized via `normalize_pm_name`. Substring
    matching is intentional: "Keller Williams Realty Phoenix" normalizes to
    "keller williams realty" and matches the "keller williams" entry.
    """
    if not normalized_name:
        return False
    n = normalized_name.lower().strip()
    for brokerage in _BROKERAGES_NORMALIZED:
        if brokerage and brokerage in n:
            return True
    return False


def match_institutional_landlord(normalized_name: str) -> str | None:
    """Return the canonical institutional-landlord display name, or None.

    Input must already be normalized via `normalize_pm_name`. Substring match
    against each alias; returns the first hit.
    """
    if not normalized_name:
        return None
    n = normalized_name.lower().strip()
    for canonical, aliases in _INSTITUTIONAL_NORMALIZED.items():
        for alias in aliases:
            if alias and alias in n:
                return canonical
    return None
