# """
# This script enriches vendor data with geocoding information using the OpenCage Geocoder API.
# It reads vendor data from a JSON input file, performs geocoding to fetch address, city, and country
# information, and writes the enriched data to a JSON output file. Vendors without sufficient location
# information (e.g., missing address or city) are enriched based on their name and a default location
# (Sicily, Italy).

# Steps:
# 1. Load vendor data from the input JSON file.
# 2. Perform geocoding for vendors with missing location details.
# 3. Update the vendor data with formatted address, city, and country.
# 4. Save the enriched data to the output JSON file.

# Dependencies:
# - OpenCage Geocoder API (requires an API key stored in the `.env` file as `open_cage_api_key`).

# Output:
# - Enriched vendor data is saved to the specified output JSON file.
# """
# from opencage.geocoder import OpenCageGeocode
# import json
# import os
# from dotenv import load_dotenv

# load_dotenv()

# geocoder = OpenCageGeocode(os.getenv("open_cage_api_key"))


# def enrich_locations(input_file, output_file):
#     try:
#         with open(input_file, "r") as f:
#             vendors = json.load(f)
#     except FileNotFoundError:
#         print(f"Warning: Input file '{input_file}' not found. Skipping enrichment.")
#         return
    
#     for vendor in vendors:
#         if not vendor.get("address") or not vendor.get("city"):
#             query = vendor.get("name") + ", Sicily, Italy"
#             result = geocoder.geocode(query)
#             if result:
#                 components = result[0]["components"]
#                 vendor["address"] = result[0]["formatted"]
#                 vendor["city"] = components.get("city", "Unknown")
#                 vendor["country"] = components.get("country", "Italy")
    
#     try:
#         with open(output_file, "w") as f:
#             json.dump(vendors, f)
#         print(f"Enriched {len(vendors)} vendors with OpenCage.")
#     except FileNotFoundError:
#         print(f"Warning: Output file '{output_file}' could not be created.")

# if __name__ == "__main__":

#     # build paths relative to this script's directory
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     osm_input_path = os.path.join(base_dir, "outputs", "osm_vendors.json")
#     osm_output_path = os.path.join(base_dir, "outputs", "osm_enriched.json")
#     yelp_fsq_input_path = os.path.join(base_dir, "outputs", "yelp_fsq_vendors.json")
#     yelp_fsq_output_path = os.path.join(base_dir, "outputs", "yelp_fsq_enriched.json")

#     # Enrich both OSM and Yelp/Foursquare data    
#     enrich_locations(osm_input_path, osm_output_path)
#     enrich_locations(yelp_fsq_input_path, yelp_fsq_output_path)

"""
This script enriches vendor data with geocoding information using the OpenCage Geocoder API.
It reads vendor data from a JSON input file, performs geocoding to fetch address, city, and country
information, and writes the enriched data to a JSON output file. Vendors without sufficient location
information (e.g., missing address or city) are enriched based on their name and a default location
(Sicily, Italy).

Steps:
1. Load vendor data from the input JSON file.
2. Perform geocoding for vendors with missing location details.
3. Update the vendor data with formatted address, city, and country.
4. Save the enriched data to the output JSON file.

Dependencies:
- OpenCage Geocoder API (requires an API key stored in the `.env` file as `open_cage_api_key`).

Output:
- Enriched vendor data is saved to the specified output JSON file.
"""

# geocode_opencage.py
import json
import os
import time
import logging
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import OpenCageGeocodeError

# Optional: if you want bbox biasing for Sicily
try:
    import config
    SICILY_BBOX = getattr(config, "SICILY_BBOX", None)
except Exception:
    SICILY_BBOX = None

load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Load API key (support both env var names)
API_KEY = os.getenv("open_cage_api_key") or os.getenv("OPENCAGE_API_KEY")
if not API_KEY:
    logger.warning("OpenCage API key not found in environment (open_cage_api_key or OPENCAGE_API_KEY).")

geocoder = OpenCageGeocode(API_KEY) if API_KEY else None

# Respect OpenCage free-tier rate limit (~1 req/sec)
OPENCAGE_DELAY_SECONDS = float(os.getenv("OPENCAGE_DELAY_SECONDS", "1.2"))

# Simple in-memory cache to avoid repeated lookups within a run
REVERSE_CACHE: Dict[Tuple[float, float], Dict[str, Any]] = {}
FORWARD_CACHE: Dict[str, Dict[str, Any]] = {}


def _ensure_output_dir(path: str) -> None:
    """
    Ensure the directory for the given file path exists.

    Args:
        path: The file path whose directory should exist.
    """
    out_dir = os.path.dirname(os.path.abspath(path))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)


def _load_json(path: str) -> List[Dict[str, Any]]:
    """
    Load a JSON list of vendor dicts from disk.

    Args:
        path: Input JSON file path.

    Returns:
        List of vendor dicts. Empty list if file missing or invalid.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            logger.info(f"Loaded {len(data)} vendors from {path}")
            return data
        logger.error(f"Input file {path} did not contain a JSON list.")
        return []
    except FileNotFoundError:
        logger.warning(f"Input file '{path}' not found. Skipping enrichment.")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from '{path}': {e}")
        return []


def _save_json(path: str, data: List[Dict[str, Any]]) -> None:
    """
    Save the list of vendor dicts to disk as pretty JSON.

    Args:
        path: Output JSON file path.
        data: List of vendor dicts.
    """
    _ensure_output_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Wrote {len(data)} vendors -> {path}")


def _best_city(components: Dict[str, Any]) -> str:
    """
    Choose the most appropriate city-like component from OpenCage components.

    Args:
        components: The 'components' dict from an OpenCage result.

    Returns:
        City/town/village/municipality/county string, or empty string.
    """
    for key in ("city", "town", "village", "municipality", "county", "state_district"):
        val = components.get(key)
        if val:
            return val
    return ""


def _apply_result_to_vendor(vendor: Dict[str, Any], result: Dict[str, Any]) -> None:
    """
    Update vendor fields using a single OpenCage geocoding result.

    Args:
        vendor: Vendor dict to be updated.
        result: A single result object from OpenCage.
    """
    components = result.get("components", {}) or {}
    geometry = result.get("geometry", {}) or {}

    # Formatted address is helpful; can be long but consistent
    formatted = result.get("formatted")
    if formatted:
        vendor["address"] = formatted

    # City and country
    if not vendor.get("city"):
        vendor["city"] = _best_city(components)
    if components.get("postcode"):
        vendor["postcode"] = components.get("postcode")
    if components.get("state"):
        vendor["state"] = components.get("state")
    if components.get("country"):
        vendor["country"] = components.get("country")

    # Coordinates (only set if missing to avoid overriding source coords)
    if vendor.get("lat") in (None, "") and geometry.get("lat") is not None:
        vendor["lat"] = float(geometry.get("lat"))
    if vendor.get("lon") in (None, "") and geometry.get("lng") is not None:
        vendor["lon"] = float(geometry.get("lng"))


def _sicily_bounds() -> Optional[Tuple[float, float, float, float]]:
    """
    Return Sicily bounding box as a tuple (south, west, north, east) if available.

    Returns:
        Bounds tuple or None if not configured.
    """
    if not SICILY_BBOX:
        return None
    try:
        s, w, n, e = map(float, SICILY_BBOX.split(","))
        return (s, w, n, e)
    except Exception:
        logger.debug("Invalid SICILY_BBOX format; expected 'south,west,north,east'.")
        return None


def _reverse_geocode(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Perform a reverse geocode on coordinates.

    Args:
        lat: Latitude.
        lon: Longitude.

    Returns:
        The top OpenCage result dict or None.
    """
    if not geocoder:
        return None

    key = (round(float(lat), 6), round(float(lon), 6))
    if key in REVERSE_CACHE:
        return REVERSE_CACHE[key]

    try:
        results = geocoder.reverse_geocode(
            lat, lon,
            language="it",
            no_annotations=1,
            limit=1,
        )
        time.sleep(OPENCAGE_DELAY_SECONDS)
        if results:
            REVERSE_CACHE[key] = results[0]
            return results[0]
    except OpenCageGeocodeError as e:
        logger.warning(f"Reverse geocode error for {lat},{lon}: {e}")
    except Exception as e:
        logger.warning(f"Unexpected error during reverse geocode for {lat},{lon}: {e}")
    return None


def _forward_geocode(query: str, bounds: Optional[Tuple[float, float, float, float]]) -> Optional[Dict[str, Any]]:
    """
    Perform a forward geocode on a text query, biased to Sicily and Italy.

    Args:
        query: Text query (e.g., 'Name, Sicily, Italy' or address).
        bounds: Optional bounding box bias (south, west, north, east).

    Returns:
        The top OpenCage result dict or None.
    """
    if not geocoder:
        return None

    if query in FORWARD_CACHE:
        return FORWARD_CACHE[query]

    kwargs = dict(
        countrycode="it",
        language="it",
        no_annotations=1,
        limit=1,
    )
    if bounds:
        # OpenCage expects min lon, min lat, max lon, max lat
        s, w, n, e = bounds
        kwargs["bounds"] = f"{w},{s},{e},{n}"

    try:
        results = geocoder.geocode(query, **kwargs)
        time.sleep(OPENCAGE_DELAY_SECONDS)
        if results:
            FORWARD_CACHE[query] = results[0]
            return results[0]
    except OpenCageGeocodeError as e:
        logger.warning(f"Forward geocode error for '{query}': {e}")
    except Exception as e:
        logger.warning(f"Unexpected error during forward geocode for '{query}': {e}")
    return None


def _enrich_single_vendor(vendor: Dict[str, Any], bounds: Optional[Tuple[float, float, float, float]]) -> str:
    """
    Enrich a single vendor in place using reverse or forward geocoding.

    Strategy:
      - If lat/lon exist: reverse geocode to normalize address components.
      - Else if address or city exists: forward geocode using that text.
      - Else: forward geocode using name + 'Sicilia, Italy' as a broad hint.

    Args:
        vendor: The vendor dict (modified in place).
        bounds: Optional bbox bias for forward geocoding.

    Returns:
        A short status string describing the action taken.
    """
    lat = vendor.get("lat")
    lon = vendor.get("lon")

    # Prefer reverse geocoding when we have coordinates
    if lat is not None and lon is not None:
        res = _reverse_geocode(float(lat), float(lon))
        if res:
            _apply_result_to_vendor(vendor, res)
            return "reverse"
        return "reverse_failed"

    # Forward geocode with available address context
    q_parts = []
    if vendor.get("address"):
        q_parts.append(str(vendor["address"]))
    if vendor.get("city"):
        q_parts.append(str(vendor["city"]))
    q_parts.append("Sicilia, Italy")
    query = ", ".join([p for p in q_parts if p])

    # If still empty, fall back to name + Sicilia, Italy
    if not vendor.get("address") and not vendor.get("city"):
        name = vendor.get("name") or ""
        query = f"{name}, Sicilia, Italy".strip(", ")

    res = _forward_geocode(query, bounds)
    if res:
        _apply_result_to_vendor(vendor, res)
        return "forward"
    return "forward_failed"


def enrich_locations(input_file: str, output_file: str) -> None:
    """
    Enrich vendors from input_file with geocoded address components and write to output_file.

    - Reads vendors (expects a JSON list of dicts).
    - For each vendor, applies reverse geocoding if coordinates exist; otherwise, forward geocoding.
    - Updates address/city/postcode/country (and state) and coordinates if missing.
    - Writes enriched list to output file.

    Args:
        input_file: Path to the input vendor JSON.
        output_file: Path to write the enriched JSON.
    """
    if not geocoder:
        logger.error("OpenCage geocoder not initialized because the API key is missing. Skipping.")
        return

    vendors = _load_json(input_file)
    if not vendors:
        logger.info("No vendors to enrich.")
        return

    bounds = _sicily_bounds()
    if bounds:
        logger.debug(f"Using Sicily bbox bias: south={bounds[0]}, west={bounds[1]}, north={bounds[2]}, east={bounds[3]}")

    reverse_ok = forward_ok = reverse_fail = forward_fail = 0

    for idx, vendor in enumerate(vendors, start=1):
        osm_id = vendor.get("osm_id") or vendor.get("id") or "unknown_id"
        name = vendor.get("name") or "Unknown"

        status = _enrich_single_vendor(vendor, bounds)
        if status == "reverse":
            reverse_ok += 1
            logger.debug(f"[{idx}/{len(vendors)}] Reverse geocoded: {name} ({osm_id})")
        elif status == "forward":
            forward_ok += 1
            logger.debug(f"[{idx}/{len(vendors)}] Forward geocoded: {name} ({osm_id})")
        elif status == "reverse_failed":
            reverse_fail += 1
            logger.debug(f"[{idx}/{len(vendors)}] Reverse failed: {name} ({osm_id})")
        elif status == "forward_failed":
            forward_fail += 1
            logger.debug(f"[{idx}/{len(vendors)}] Forward failed: {name} ({osm_id})")
        else:
            logger.debug(f"[{idx}/{len(vendors)}] No geocode action: {name} ({osm_id})")

        # Periodic progress at INFO level
        if idx % 50 == 0:
            logger.info(f"Progress: {idx}/{len(vendors)} processed "
                        f"(rev_ok={reverse_ok}, fwd_ok={forward_ok}, rev_fail={reverse_fail}, fwd_fail={forward_fail})")

    logger.info(f"Enrichment complete: total={len(vendors)}, "
                f"rev_ok={reverse_ok}, fwd_ok={forward_ok}, rev_fail={reverse_fail}, fwd_fail={forward_fail}")

    _save_json(output_file, vendors)


if __name__ == "__main__":
    # Build paths relative to this script's directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    osm_input_path = os.path.join(base_dir, "outputs", "osm_vendors.json")
    osm_output_path = os.path.join(base_dir, "outputs", "osm_enriched.json")
    yelp_fsq_input_path = os.path.join(base_dir, "outputs", "yelp_fsq_vendors.json")
    yelp_fsq_output_path = os.path.join(base_dir, "outputs", "yelp_fsq_enriched.json")

    # Enrich both OSM and Yelp/Foursquare data
    enrich_locations(osm_input_path, osm_output_path)
    enrich_locations(yelp_fsq_input_path, yelp_fsq_output_path)