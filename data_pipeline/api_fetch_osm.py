# api_fetch_osm.py
import os
import json
import time
import overpy
import config
from dotenv import load_dotenv

load_dotenv()

# Overpass client with some retry resilience
api = overpy.Overpass(max_retry_count=3, retry_timeout=10)

# Read OSM filters from config
OSM_FILTERS = config.OSM_TAGS

# Name regex to capture Italian/English wedding words in POI names
NAME_REGEX = r"(spos|sposa|sposi|nozz|matrimoni|matrimonio|wedding)"


def _build_overpass_query() -> str:
    """
    Build an Overpass QL query for Sicily (ISO3166-2=IT-82) that returns nodes/ways/relations
    matching configured OSM filters, plus a name-based fallback regex for wedding keywords.

    Returns:
        str: The complete Overpass QL query string.
    """
    parts = []
    for k, v in OSM_FILTERS:
        parts.append(f'nwr(area.a)["{k}"="{v}"];')
    # Fallback: any POI whose name mentions weddings (Italian / English)
    parts.append(f'nwr(area.a)["name"~"{NAME_REGEX}", i];')

    union = "\n  ".join(parts)
    query = f"""
[out:json][timeout:180];
area["ISO3166-2"="IT-82"]->.a;
(
  {union}
);
out body center qt;
"""
    return query


def _extract_contact(tags: dict, key: str) -> str:
    """
    Extract a contact field, prioritizing contact:* namespaced tags.

    Args:
        tags (dict): OSM tags.
        key (str): Contact key such as 'phone', 'email', 'website'.

    Returns:
        str: The contact value or empty string.
    """
    return tags.get(f"contact:{key}") or tags.get(key) or ""


def _extract_city(tags: dict) -> str:
    """
    Extract a best-effort city-like value from address tags.

    Args:
        tags (dict): OSM tags.

    Returns:
        str: City/town/village value or empty string.
    """
    return tags.get("addr:city") or tags.get("addr:town") or tags.get("addr:village") or ""


def _extract_address_line(tags: dict) -> str:
    """
    Build a single-line street address from street and housenumber when available.

    Args:
        tags (dict): OSM tags.

    Returns:
        str: Address line.
    """
    street = tags.get("addr:street", "")
    housenumber = tags.get("addr:housenumber", "")
    if street and housenumber:
        return f"{street} {housenumber}"
    return street or housenumber or ""


def _service_type(tags: dict) -> str:
    """
    Determine a service type using common OSM keys.

    Args:
        tags (dict): OSM tags.

    Returns:
        str: Service type derived from shop/amenity/craft, or 'unknown'.
    """
    return tags.get("shop") or tags.get("amenity") or tags.get("craft") or "unknown"


def _plain_raw_tags(tags: dict) -> dict:
    """
    Convert overpy tags mapping to a plain JSON-serializable dict with string values.

    Args:
        tags (dict): OSM tags (may be a custom mapping class from overpy).

    Returns:
        dict: Plain dict with stringified values, safe for JSON serialization.
    """
    if not tags:
        return {}
    out = {}
    for k, v in tags.items():
        if isinstance(v, (list, tuple, set)):
            out[str(k)] = ", ".join(map(str, v))
        else:
            out[str(k)] = "" if v is None else str(v)
    return out


def _to_vendor(obj) -> dict:
    """
    Normalize an overpy Node/Way/Relation into a vendor dictionary.

    Args:
        obj: overpy.Node, overpy.Way, or overpy.Relation.

    Returns:
        dict: Normalized vendor record with coordinates and selected tags.
    """
    tags = obj.tags
    name = tags.get("name") or tags.get("brand") or "Unknown"
    service = _service_type(tags)

    # Coordinates + OSM id
    lat = None
    lon = None
    osm_id = None
    if isinstance(obj, overpy.Node):
        lat = float(obj.lat)
        lon = float(obj.lon)
        osm_id = f"node/{obj.id}"
    elif isinstance(obj, overpy.Way):
        # Requires 'out center' in query to be present
        lat = getattr(obj, "center_lat", None)
        lon = getattr(obj, "center_lon", None)
        osm_id = f"way/{obj.id}"
    else:  # Relation
        lat = getattr(obj, "center_lat", None)
        lon = getattr(obj, "center_lon", None)
        osm_id = f"relation/{obj.id}"

    vendor = {
        "source": "OSM",
        "osm_id": osm_id,
        "name": name,
        "service_type": service,
        "address": _extract_address_line(tags),
        "city": _extract_city(tags),
        "postcode": tags.get("addr:postcode", ""),
        "country": "Italy",
        "lat": float(lat) if lat is not None else None,
        "lon": float(lon) if lon is not None else None,
        "phone": _extract_contact(tags, "phone"),
        "email": _extract_contact(tags, "email"),
        "website": _extract_contact(tags, "website"),
        "instagram": tags.get("contact:instagram", ""),
        "facebook": tags.get("contact:facebook", ""),
        "opening_hours": tags.get("opening_hours", ""),
        "raw_tags": _plain_raw_tags(tags),  # ensure JSON-serializable
    }
    return vendor


def fetch_osm_data() -> None:
    """
    Execute the Overpass query for Sicily, normalize results into vendor records,
    deduplicate by OSM id, and write them to outputs/osm_vendors.json.

    Side effects:
        - Creates the outputs directory if missing.
        - Writes outputs/osm_vendors.json.
    """
    os.makedirs("outputs", exist_ok=True)
    query = _build_overpass_query()

    # Run query with a simple rate-limit retry
    try:
        result = api.query(query)
    except overpy.exception.OverpassTooManyRequests:
        time.sleep(20)
        result = api.query(query)

    # Convert to normalized vendors and deduplicate by osm_id
    vendors_by_id = {}

    for n in result.nodes:
        v = _to_vendor(n)
        vendors_by_id[v["osm_id"]] = v

    for w in result.ways:
        v = _to_vendor(w)
        vendors_by_id[v["osm_id"]] = v

    for r in result.relations:
        v = _to_vendor(r)
        vendors_by_id[v["osm_id"]] = v

    vendors = list(vendors_by_id.values())

    # # Save
    # out_path = "outputs/osm_vendors.json"
    # with open(out_path, "w", encoding="utf-8") as f:
    #     json.dump(vendors, f, ensure_ascii=False, indent=2)

    # Save
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "osm_vendors.json")

    print(f"Writing {len(vendors)} OSM vendors to {out_path}...")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(vendors, f, ensure_ascii=False, indent=2)

    print(f"Fetched {len(vendors)} OSM vendors for Sicily -> {out_path}")


if __name__ == "__main__":
    # For debugging: uncomment to inspect query
    print(_build_overpass_query())
    fetch_osm_data()