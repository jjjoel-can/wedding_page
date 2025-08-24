# compare_sources.py
import os
import json
import logging
import argparse
import unicodedata
from typing import Any, Dict, List, Tuple, Optional
from collections import Counter

import pandas as pd

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _abs_path(*parts) -> str:
    """
    Build an absolute path relative to this script's directory.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def _load_json(path: str) -> List[Dict[str, Any]]:
    """
    Load a JSON list safely. Returns empty list if missing or malformed.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            logger.error(f"File {path} does not contain a JSON list.")
            return []
        logger.info(f"Loaded {len(data)} records from {path}")
        return data
    except FileNotFoundError:
        logger.warning(f"Input file not found: {path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from {path}: {e}")
        return []


def _normalize_text(s: Optional[str]) -> str:
    """
    Normalize a string for comparison: lowercase, strip, remove diacritics and punctuation,
    and drop common company suffixes.
    """
    if not s:
        return ""
    s = s.strip().lower()

    # Remove accents
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

    # Replace punctuation with spaces
    punct = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    s = s.translate(str.maketrans({c: " " for c in punct}))

    # Collapse whitespace
    s = " ".join(s.split())

    # Remove common company tokens
    tokens = s.split()
    drop = {
        "srl", "s.r.l.", "spa", "s.p.a.", "sas", "snc", "ltd", "co", "inc",
        "di", "del", "della", "dei", "degli", "studio", "the"
    }
    tokens = [t for t in tokens if t not in drop]
    return " ".join(tokens)


def _round_or_none(v: Any, decimals: int = 3) -> Optional[float]:
    """
    Safely round numeric value or return None.
    """
    try:
        return round(float(v), decimals)
    except Exception:
        return None


def _vendor_key(v: Dict[str, Any]) -> Tuple:
    """
    Build a grouping key for a vendor:
      - If lat/lon available: ('geo', round(lat, 3), round(lon, 3), name_norm)
      - Else: ('namecity', name_norm, city_norm)
    """
    name_norm = _normalize_text(v.get("name"))
    city_norm = _normalize_text(v.get("city"))
    lat = _round_or_none(v.get("lat"), 3)
    lon = _round_or_none(v.get("lon"), 3)

    if lat is not None and lon is not None and name_norm:
        return ("geo", lat, lon, name_norm)
    return ("namecity", name_norm, city_norm)


def _coerce_source(v: Dict[str, Any]) -> str:
    """
    Return a clean source label among {'OSM', 'Yelp', 'Foursquare', 'Unknown'}.
    """
    s = (v.get("source") or "").strip().lower()
    if "osm" in s:
        return "OSM"
    if "yelp" in s:
        return "Yelp"
    if "foursquare" in s or "fsq" in s:
        return "Foursquare"
    return "Unknown"


def _group_vendors(vendors: List[Dict[str, Any]]) -> Dict[Tuple, Dict[str, Any]]:
    """
    Group vendors by the vendor key. Aggregates sources per group.
    """
    groups: Dict[Tuple, Dict[str, Any]] = {}
    for v in vendors:
        key = _vendor_key(v)
        src = _coerce_source(v)
        g = groups.setdefault(key, {"samples": [], "sources": set()})
        g["samples"].append(v)
        g["sources"].add(src)
    return groups


def _unique_count_by_source(vendors: List[Dict[str, Any]], source: str) -> int:
    """
    Count unique vendors for a single source using the same grouping key
    (restricted to that source’s items).
    """
    subset = [v for v in vendors if _coerce_source(v) == source]
    grouped = _group_vendors(subset)
    return len(grouped)


def _representative_name(samples: List[Dict[str, Any]]) -> str:
    """
    Pick a representative vendor name from grouped samples.
    Prefer the most frequent non-empty name; fallback to 'Unknown'.
    """
    names = [str(s.get("name") or "").strip() for s in samples if (s.get("name") or "").strip()]
    if not names:
        return "Unknown"
    counts = Counter(names)
    best, _ = counts.most_common(1)[0]
    return best


def _build_presence_dataframe(groups: Dict[Tuple, Dict[str, Any]]) -> pd.DataFrame:
    """
    Build a presence matrix DataFrame:
    columns: vendor, yelp, foursquare, osm (1 if group contains that source, else 0).
    """
    rows = []
    for g in groups.values():
        name = _representative_name(g["samples"])
        srcs = g["sources"]
        rows.append({
            "vendor": name,
            "yelp": 1 if "Yelp" in srcs else 0,
            "foursquare": 1 if "Foursquare" in srcs else 0,
            "osm": 1 if "OSM" in srcs else 0,
        })
    df = pd.DataFrame(rows, columns=["vendor", "yelp", "foursquare", "osm"])
    return df


def compare_sources(osm_file: str, yelp_fsq_file: str) -> pd.DataFrame:
    """
    Compare OSM vs Yelp vs Foursquare coverage, log summary stats, build presence matrix,
    and save it to sources/sources_comparison.csv.

    Returns:
      pandas DataFrame with columns [vendor, yelp, foursquare, osm]
    """
    osm = _load_json(osm_file)
    yfs = _load_json(yelp_fsq_file)

    all_vendors: List[Dict[str, Any]] = []

    # Ensure OSM items have a 'source'
    for v in osm:
        if not v.get("source"):
            v["source"] = "OSM"
    all_vendors.extend(osm)

    # Yelp/FSQ combined list (expects 'source' per item)
    all_vendors.extend(yfs)

    # Unique per source
    osm_unique = _unique_count_by_source(all_vendors, "OSM")
    yelp_unique = _unique_count_by_source(all_vendors, "Yelp")
    fsq_unique = _unique_count_by_source(all_vendors, "Foursquare")

    logger.info("Unique vendors per source:")
    logger.info(f"  OSM: {osm_unique}")
    logger.info(f"  Yelp: {yelp_unique}")
    logger.info(f"  Foursquare: {fsq_unique}")

    # Global grouping and overlaps
    groups = _group_vendors(all_vendors)
    total_unique = len(groups)

    def has_source(g, s): return s in g["sources"]
    yelp_osm = sum(1 for g in groups.values() if has_source(g, "Yelp") and has_source(g, "OSM"))
    fsq_osm = sum(1 for g in groups.values() if has_source(g, "Foursquare") and has_source(g, "OSM"))
    yelp_fsq = sum(1 for g in groups.values() if has_source(g, "Yelp") and has_source(g, "Foursquare"))
    triple = sum(1 for g in groups.values()
                 if has_source(g, "Yelp") and has_source(g, "Foursquare") and has_source(g, "OSM"))
    multi_api_count = sum(1 for g in groups.values() if len(g["sources"] - {"Unknown"}) >= 2)

    logger.info(f"Total unique vendors across all sources: {total_unique}")
    logger.info(f"Vendors found by multiple APIs (>=2): {multi_api_count}")
    logger.info(f"Pairwise overlaps: Yelp∩OSM={yelp_osm}, FSQ∩OSM={fsq_osm}, Yelp∩FSQ={yelp_fsq}")
    logger.info(f"Triple overlap (Yelp ∩ Foursquare ∩ OSM): {triple}")

    # Build DataFrame
    df = _build_presence_dataframe(groups)
    logger.info(f"Presence matrix shape: {df.shape}")

    # Save DataFrame to sources/sources_comparison.csv
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sources_dir = os.path.join(base_dir, "outputs")
    os.makedirs(sources_dir, exist_ok=True)
    csv_path = os.path.join(sources_dir, "sources_comparison.csv")
    df.to_csv(csv_path, index=False)
    logger.info(f"Saved sources comparison matrix -> {csv_path}")

    return df


def main():
    parser = argparse.ArgumentParser(description="Compare vendor coverage across OSM, Yelp, and Foursquare.")
    parser.add_argument("--osm", default=_abs_path("outputs", "osm_enriched.json"),
                        help="Path to OSM enriched JSON")
    parser.add_argument("--yelpfsq", default=_abs_path("outputs", "yelp_fsq_enriched.json"),
                        help="Path to Yelp/Foursquare enriched JSON")
    args = parser.parse_args()

    compare_sources(args.osm, args.yelpfsq)


if __name__ == "__main__":
    main()