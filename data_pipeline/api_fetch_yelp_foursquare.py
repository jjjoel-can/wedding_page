
# import requests
# import json
# from yelpapi import YelpAPI
# import config
# from dotenv import load_dotenv
# import logging
# import os
# import sys

# # Configure logging
# #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Logs only to a file named 'app.log' in the same directory
# logging.basicConfig(
#     filename='outputs/api_fetch_yelp_foursquare.log',
#     filemode='a',  # 'a' for append, 'w' for overwrite
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# # Load environment variables from .env file
# load_dotenv()

# # --- API Key Validation ---
# YELP_API_KEY = os.getenv("yelp_api_key")
# FSQ_API_KEY = os.getenv("four_square_api_key")

# if not YELP_API_KEY:
#     logging.error("Yelp API key not found. Make sure it's set in your .env file.")
#     sys.exit("Exiting: Missing Yelp API Key.")
# if not FSQ_API_KEY:
#     logging.error("Foursquare API key not found. Make sure it's set in your .env file as 'four_square_api_key'.")
#     sys.exit("Exiting: Missing Foursquare API Key.")

# # Initialize Yelp API client
# yelp_api = YelpAPI(YELP_API_KEY)

# # Dynamically construct the path relative to the current script's directory
# output_path = os.path.join(os.path.dirname(__file__), "outputs", "yelp_fsq_vendors.json")
# # Ensure the output directory exists
# os.makedirs(os.path.dirname(output_path), exist_ok=True)

# def test_foursquare_auth():
#     """Test if Foursquare API key is working"""
#     #url = "https://api.foursquare.com/v3/places/search"
#     url = "https://places-api.foursquare.com/places/search"
#     # headers = {
#     #     "Authorization": f"Bearer {FSQ_API_KEY}",
#     #     "accept": "application/json"
#     # }

#     headers = {
#         "accept": "application/json",
#         "X-Places-Api-Version": "2025-06-17",
#         "authorization": f"Bearer {FSQ_API_KEY}" # Added "Bearer " prefix
#     }
#     params = {"query": "restaurant", "near": "New York, NY", "limit": 1}
    
#     try:
#         response = requests.get(url, params=params, headers=headers)
#         response.raise_for_status()
#         data = response.json()
#         print(f"✅ Foursquare API is working! Found {len(data.get('results', []))} results")
#         return True
#     except Exception as e:
#         print(f"❌ Foursquare API test failed: {e}")
#         return False


# def fetch_yelp_data():
#     ''' Fetches wedding vendors from Yelp for specified cities and categories.'''
#     vendors = []
#     logging.info("Starting Yelp data fetch...")
#     for city in config.SICILY_CITIES:
#         for category in config.WEDDING_CATEGORIES:
#             try:
#                 # The Yelp Fusion API is used for business searches. [docs.developer.yelp.com](https://docs.developer.yelp.com/docs/fusion-intro)
#                 response = yelp_api.search_query(categories=category, location=f"{city}, Italy", limit=50)
#                 businesses = response.get("businesses", [])
#                 for biz in businesses:
#                     vendors.append({
#                         "name": biz.get("name"),
#                         "service_type": category,
#                         "address": " ".join(biz.get("location", {}).get("display_address", [])),
#                         "city": biz.get("location", {}).get("city"),
#                         "contact": biz.get("phone"),
#                         "picture_url": biz.get("image_url"),
#                         "website": biz.get("url"),
#                         "source": "Yelp"
#                     })
#                 logging.info(f"Fetched {len(businesses)} Yelp results for '{category}' in {city}")
#             except Exception as e:
#                 logging.error(f"Yelp API error for {city}/{category}: {e}")
#     return vendors

# def fetch_foursquare_data():
#     ''' Fetches wedding vendors from Foursquare for specified cities and categories. '''
#     vendors = []
#     #url = "https://api.foursquare.com/v3/places/search"
#     url = "https://places-api.foursquare.com/places/search"
    
#     # FIXED: Proper Bearer token format for Foursquare API v3
#     headers = {
#         "accept": "application/json",
#         "X-Places-Api-Version": "2025-06-17",
#         "authorization": f"Bearer {FSQ_API_KEY}" # Added "Bearer " prefix
#     }
    
#     logging.info("Starting Foursquare data fetch...")
#     for city in config.SICILY_CITIES:
#         for category in config.WEDDING_CATEGORIES:
#             # Foursquare uses a generic 'query' and a 'near' parameter for location
#             params = {"query": category, "near": f"{city}, IT", "limit": 50, "sort": "RELEVANCE"}
#             try:
#                 response = requests.get(url, params=params, headers=headers)
#                 # This will raise an HTTPError for bad responses (4xx or 5xx)
#                 response.raise_for_status() 
                
#                 data = response.json()
#                 places = data.get("results", [])
                
#                 for place in places:
#                     # Gracefully handle missing data using .get()
#                     location = place.get("location", {})
#                     vendors.append({
#                         "name": place.get("name"),
#                         "service_type": category,
#                         "address": location.get("formatted_address"),
#                         "city": location.get("locality"),
#                         "contact": None,  # Foursquare V3 Search doesn't typically return phone numbers
#                         "picture_url": None, # Foursquare V3 Search doesnt return picture urls. You need a separate call
#                         "website": None, # Foursquare V3 Search doesnt return a website. You need a separate call
#                         "source": "Foursquare"
#                     })
#                 logging.info(f"Fetched {len(places)} Foursquare results for '{category}' in {city}")
            
#             # Catch specific request exceptions for better error logging
#             except requests.exceptions.HTTPError as http_err:
#                 logging.error(f"Foursquare HTTP error for {city}/{category}: {http_err} - Response: {response.text}")
#             except requests.exceptions.RequestException as req_err:
#                 logging.error(f"Foursquare Request error for {city}/{category}: {req_err}")
#             except Exception as e:
#                 logging.error(f"An unexpected Foursquare API error occurred for {city}/{category}: {e}")
#     return vendors

# def main():
#     test_foursquare_auth()  # Test Foursquare API key before proceeding
#     #yelp_vendors = fetch_yelp_data()
#     #foursquare_vendors = fetch_foursquare_data()
    
#     all_vendors = fetch_yelp_data() + fetch_foursquare_data()
#     #all_vendors = foursquare_vendors

#     with open(output_path, "w", encoding='utf-8') as f:
#         json.dump(all_vendors, f, indent=4, ensure_ascii=False)
        
#     logging.info(f"Process complete. Fetched {len(all_vendors)} total vendors.")
#     print(f"Data saved to {output_path}")


# if __name__ == "__main__":
#     main()


# api_fetch_yelp_foursquare.py
# Single consolidated script:
# - Tiles across Sicily and fetches Yelp + Foursquare results for a tight "wedding value chain"
# - Handles pagination, retries, deduplication, progress logging, partial saves
# - Saves merged output to outputs/yelp_fsq_vendors.json

# api_fetch_yelp_foursquare.py
# Tiles across Sicily and fetches Yelp + Foursquare for a tight "wedding value chain"
# - Yelp: raw requests with adaptive 429 handling (cooldown, Retry-After/Reset headers)
# - FSQ: requests with retries
# - Separate pacing for Yelp/FSQ
# - Progress logs, partial saves, dedupe by source_id
# - Output -> outputs/yelp_fsq_vendors.json

# config.py
# Centralized configuration for tiling, pacing, retries, pagination,
# quick-mode limits, and search taxonomies.

# api_fetch_yelp_foursquare.py
# Uses config.py for ALL tunables.

import os
import sys
import time
import json
import logging
import requests
from typing import Dict, Any, List, Tuple, Set, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

import config  # all settings come from here

# ---- Paths and logging ----

base_dir = os.path.dirname(os.path.abspath(__file__))
outputs_dir = os.path.join(base_dir, "outputs")
os.makedirs(outputs_dir, exist_ok=True)

log_path = os.path.join(outputs_dir, "api_fetch_yelp_foursquare.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

for h in list(logger.handlers):
    logger.removeHandler(h)

fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
file_handler.setFormatter(fmt)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(fmt)
logger.addHandler(console_handler)

# ---- Environment and API headers ----

load_dotenv()
YELP_API_KEY = os.getenv("yelp_api_key")
FSQ_API_KEY = os.getenv("four_square_api_key")
if not YELP_API_KEY:
    logger.error("Yelp API key not found. Set yelp_api_key in .env or environment.")
    sys.exit(1)
if not FSQ_API_KEY:
    logger.error("Foursquare API key not found. Set four_square_api_key in .env or environment.")
    sys.exit(1)

YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"
YELP_HEADERS = {"Authorization": f"Bearer {YELP_API_KEY}"}

FSQ_SEARCH_URL = "https://places-api.foursquare.com/places/search"
FSQ_HEADERS = {
    "Accept": "application/json",
    "X-Places-Api-Version": "2024-08-01",
    "Authorization": f"Bearer {FSQ_API_KEY}",
}

output_path = os.path.join(outputs_dir, "yelp_fsq_vendors.json")

# ---- Progress/ETA helpers ----

START_TS = datetime.utcnow()
REQUESTS_MADE = 0

def _tick_request():
    global REQUESTS_MADE
    REQUESTS_MADE += 1

def _rate(elapsed_sec: float) -> float:
    return REQUESTS_MADE / max(elapsed_sec, 1e-6)

def _eta(done: int, total: int, per_sec: float) -> str:
    if total <= 0 or per_sec <= 0 or done <= 0:
        return "ETA: N/A"
    remaining = max(total - done, 0)
    secs = remaining / per_sec
    return f"ETA: {str(timedelta(seconds=int(secs)))}"

# ---- Geo helpers using config ----

def _generate_tile_centers() -> List[Tuple[float, float]]:
    s, w, n, e = config.sicily_bbox_tuple()
    centers: List[Tuple[float, float]] = []

    lat_step = config.degree_step_lat(config.TILE_RADIUS_METERS) * config.TILE_STEP_FRACTION
    if lat_step <= 0:
        raise ValueError("Computed lat_step <= 0; check TILE_RADIUS_METERS/TILE_STEP_FRACTION")

    lat = s + lat_step
    while lat < n - lat_step:
        lon_step = config.degree_step_lon(config.TILE_RADIUS_METERS, lat) * config.TILE_STEP_FRACTION
        if lon_step <= 0:
            raise ValueError("Computed lon_step <= 0; check TILE_RADIUS_METERS/TILE_STEP_FRACTION")
        lon = w + lon_step
        while lon < e - lon_step:
            centers.append((round(lat, 6), round(lon, 6)))
            if config.QUICK_MAX_TILES and len(centers) >= config.QUICK_MAX_TILES:
                logger.info(f"QUICK mode: limiting centers to {config.QUICK_MAX_TILES}")
                return centers
            lon += lon_step
        lat += lat_step

    logger.info(f"Tiling generated {len(centers)} centers over Sicily "
                f"(radius={config.TILE_RADIUS_METERS}m, step_frac={config.TILE_STEP_FRACTION})")
    return centers

def _inside_bbox(lat: Optional[float], lon: Optional[float]) -> bool:
    if lat is None or lon is None:
        return True
    s, w, n, e = config.sicily_bbox_tuple()
    return (s - 0.05) <= lat <= (n + 0.05) and (w - 0.05) <= lon <= (e + 0.05)

# ---- Utility helpers ----

def _sleep(delay: float):
    try:
        time.sleep(delay)
    except Exception:
        pass

def _retry_loop(name: str, func, *args, **kwargs):
    """
    Retry loop with exponential backoff for transient FSQ errors (429/5xx).
    """
    for attempt in range(config.MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else None
            if status in (429, 500, 502, 503, 504):
                delay = config.BACKOFF_BASE_SECONDS * (2 ** attempt)
                logger.warning(f"{name}: HTTP {status}, retry in {delay:.1f}s (attempt {attempt+1}/{config.MAX_RETRIES})")
                _sleep(delay)
                continue
            logger.error(f"{name}: HTTP error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            delay = config.BACKOFF_BASE_SECONDS * (2 ** attempt)
            logger.warning(f"{name}: Request error: {e}, retry in {delay:.1f}s (attempt {attempt+1}/{config.MAX_RETRIES})")
            _sleep(delay)
            continue
    raise RuntimeError(f"{name}: exhausted retries")

def _normalize_vendor(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "name": record.get("name"),
        "service_type": record.get("service_type"),
        "address": record.get("address"),
        "city": record.get("city"),
        "postcode": record.get("postcode"),
        "state": record.get("state"),
        "country": record.get("country"),
        "contact": record.get("contact"),
        "picture_url": record.get("picture_url"),
        "website": record.get("website"),
        "lat": record.get("lat"),
        "lon": record.get("lon"),
        "source": record.get("source"),
        "source_id": record.get("source_id"),
    }

# ---- Yelp: adaptive 429 handling ----

LAST_YELP_REQ_TS = 0.0
YELP_CONSEC_429 = 0

def _respect_yelp_interval():
    global LAST_YELP_REQ_TS
    now = time.monotonic()
    wait = config.YELP_REQUEST_DELAY_SECONDS - (now - LAST_YELP_REQ_TS)
    if wait > 0:
        _sleep(wait)
    LAST_YELP_REQ_TS = time.monotonic()

def _yelp_search(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Yelp search with adaptive handling:
    - Enforces min interval between requests.
    - On 429: uses Retry-After / Reset headers or a configured cooldown.
    - Stops Yelp if too many consecutive 429s.
    """
    global YELP_CONSEC_429

    while True:
        _respect_yelp_interval()
        r = requests.get(YELP_SEARCH_URL, headers=YELP_HEADERS, params=params, timeout=15)
        _tick_request()

        if r.status_code == 200:
            YELP_CONSEC_429 = 0
            rem = r.headers.get("RateLimit-Remaining") or r.headers.get("X-RateLimit-Remaining")
            if rem is not None:
                try:
                    if int(rem) <= 0:
                        logger.warning("Yelp RateLimit-Remaining=0; stopping Yelp fetch for this run.")
                        return {"businesses": []}
                except Exception:
                    pass
            return r.json()

        if r.status_code == 429:
            YELP_CONSEC_429 += 1
            retry_after = r.headers.get("Retry-After")
            reset = r.headers.get("RateLimit-ResetTime") or r.headers.get("X-RateLimit-Reset")
            cooldown = config.YELP_429_COOLDOWN_SECONDS

            if retry_after:
                try:
                    cooldown = max(cooldown, int(float(retry_after)))
                except Exception:
                    pass
            elif reset:
                try:
                    reset_sec = int(float(reset))
                    if reset_sec > 1e9:
                        reset_sec = reset_sec / 1000
                    delta = int(reset_sec - time.time())
                    if delta > 0:
                        cooldown = max(cooldown, min(delta, 1800))
                except Exception:
                    pass

            logger.warning(f"Yelp 429 Too Many Requests. Sleeping {cooldown}s "
                           f"(consecutive_429={YELP_CONSEC_429}). Params: {params}")
            _sleep(cooldown)

            if YELP_CONSEC_429 >= config.YELP_MAX_CONSECUTIVE_429:
                logger.error("Yelp: too many consecutive 429s. Stopping Yelp fetch for this run.")
                return {"businesses": []}
            continue

        try:
            r.raise_for_status()
        except Exception as e:
            logger.error(f"Yelp HTTP error {r.status_code}: {e} - URL: {r.url} - Body: {r.text[:300]}")
            raise

# ---- Fetchers ----

def fetch_yelp_data_tiled() -> List[Dict[str, Any]]:
    vendors: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()
    centers = _generate_tile_centers()

    cats_full = config.YELP_CATEGORIES
    yelp_cats = cats_full[: config.QUICK_MAX_YELP_CATS or None]

    total_tiles = len(centers) * len(yelp_cats)
    logger.info(f"Yelp: {len(yelp_cats)} categories, {len(centers)} tiles (total tiles to scan: {total_tiles})")

    for ci, cat in enumerate(yelp_cats, start=1):
        for i, (lat, lon) in enumerate(centers, start=1):
            offset = 0
            added_this_tile = 0
            while offset < config.YELP_MAX_OFFSET:
                params = {
                    "latitude": lat,
                    "longitude": lon,
                    "radius": min(config.TILE_RADIUS_METERS, 40000),  # Yelp max ~40km
                    "categories": cat,
                    "limit": config.YELP_LIMIT,
                    "offset": offset,
                    "sort_by": "best_match",
                    "locale": "it_IT",
                }

                t0 = time.time()
                try:
                    resp = _yelp_search(params)
                except Exception:
                    break
                elapsed = time.time() - t0

                businesses = resp.get("businesses", []) or []
                if not businesses:
                    break

                for biz in businesses:
                    yid = biz.get("id")
                    if not yid or yid in seen_ids:
                        continue
                    seen_ids.add(yid)

                    loc = biz.get("location", {}) or {}
                    coords = biz.get("coordinates", {}) or {}

                    rec = _normalize_vendor({
                        "name": biz.get("name"),
                        "service_type": cat,
                        "address": " ".join(loc.get("display_address", []) or []),
                        "city": loc.get("city"),
                        "postcode": loc.get("zip_code"),
                        "state": loc.get("state"),
                        "country": loc.get("country"),
                        "contact": biz.get("phone"),
                        "picture_url": biz.get("image_url"),
                        "website": biz.get("url"),
                        "lat": coords.get("latitude"),
                        "lon": coords.get("longitude"),
                        "source": "Yelp",
                        "source_id": yid,
                    })
                    if _inside_bbox(rec["lat"], rec["lon"]):
                        vendors.append(rec)
                        added_this_tile += 1

                done_tiles = (ci - 1) * len(centers) + i
                rate = _rate((datetime.utcnow() - START_TS).total_seconds())
                logger.info(f"Yelp [{cat}] tile {i}/{len(centers)} offset={offset} "
                            f"req_time={elapsed:.2f}s, added_tile={added_this_tile}, total={len(vendors)}; "
                            f"tiles {done_tiles}/{total_tiles}. {_eta(done_tiles, total_tiles, rate)}")

                offset += config.YELP_LIMIT
                if len(businesses) < config.YELP_LIMIT:
                    break
                _sleep(config.YELP_REQUEST_DELAY_SECONDS)

    logger.info(f"Yelp: collected {len(vendors)} unique vendors across tiles and categories.")
    return vendors


def fetch_foursquare_data_tiled() -> List[Dict[str, Any]]:
    vendors: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()
    centers = _generate_tile_centers()

    queries_full = config.FSQ_QUERIES
    fsq_queries = queries_full[: config.QUICK_MAX_FSQ_QUERIES or None]

    total_tiles = len(centers) * len(fsq_queries)
    logger.info(f"FSQ: {len(fsq_queries)} queries, {len(centers)} tiles (total tiles to scan: {total_tiles})")

    for qi, q in enumerate(fsq_queries, start=1):
        for i, (lat, lon) in enumerate(centers, start=1):
            cursor = None
            page = 0
            while page < config.FSQ_MAX_PAGES:
                params = {
                    "ll": f"{lat},{lon}",
                    "radius": config.TILE_RADIUS_METERS,
                    "limit": config.FSQ_LIMIT,
                    "sort": "RELEVANCE",
                    "query": q,
                }
                if cursor:
                    params["cursor"] = cursor

                def _req():
                    r = requests.get(FSQ_SEARCH_URL, params=params, headers=FSQ_HEADERS, timeout=15)
                    r.raise_for_status()
                    return r

                t0 = time.time()
                try:
                    response = _retry_loop("FSQ search", _req)
                except Exception as e:
                    logger.error(f"FSQ error query='{q}' tile={i}/{len(centers)} page={page+1}: {e}")
                    break
                elapsed = time.time() - t0
                _tick_request()

                data = response.json()
                places = data.get("results", []) or []

                added_this_page = 0
                for place in places:
                    fsq_id = place.get("fsq_id")
                    if not fsq_id or fsq_id in seen_ids:
                        continue
                    seen_ids.add(fsq_id)

                    loc = place.get("location", {}) or {}
                    geocodes = place.get("geocodes", {}) or {}
                    main_geo = geocodes.get("main", {}) or {}

                    rec = _normalize_vendor({
                        "name": place.get("name"),
                        "service_type": q,
                        "address": loc.get("formatted_address")
                                  or " ".join([str(loc.get("address", "")), str(loc.get("locality", ""))]).strip(),
                        "city": loc.get("locality"),
                        "postcode": loc.get("postcode"),
                        "state": loc.get("region"),
                        "country": loc.get("country"),
                        "contact": None,
                        "picture_url": None,
                        "website": None,
                        "lat": (main_geo.get("latitude") or place.get("latitude")),
                        "lon": (main_geo.get("longitude") or place.get("longitude")),
                        "source": "Foursquare",
                        "source_id": fsq_id,
                    })
                    if _inside_bbox(rec["lat"], rec["lon"]):
                        vendors.append(rec)
                        added_this_page += 1

                cursor = data.get("next_cursor")
                page += 1

                done_tiles = (qi - 1) * len(centers) + i
                rate = _rate((datetime.utcnow() - START_TS).total_seconds())
                logger.info(f"FSQ ['{q}'] tile {i}/{len(centers)} page {page} "
                            f"req_time={elapsed:.2f}s, added_page={added_this_page}, total={len(vendors)}; "
                            f"tiles {done_tiles}/{total_tiles}. {_eta(done_tiles, total_tiles, rate)}")

                _sleep(config.FSQ_REQUEST_DELAY_SECONDS)

                if not cursor or not places:
                    break

    logger.info(f"Foursquare: collected {len(vendors)} unique vendors across tiles and queries.")
    return vendors

# ---- Misc ----

def test_foursquare_auth() -> bool:
    params = {"query": "restaurant", "near": "Palermo, IT", "limit": 1}
    try:
        r = requests.get(FSQ_SEARCH_URL, params=params, headers=FSQ_HEADERS, timeout=12)
        r.raise_for_status()
        data = r.json()
        logger.info(f"FSQ auth test OK, results={len(data.get('results', []))}")
        return True
    except Exception as e:
        logger.error(f"FSQ auth test failed: {e}")
        return False

# ---- Main ----

def main():
    logger.info("Starting Yelp/FSQ tiled fetch for Sicily.")
    logger.info(
        f"Config: radius={config.TILE_RADIUS_METERS}m, step_frac={config.TILE_STEP_FRACTION}, "
        f"FSQ_MAX_PAGES={config.FSQ_MAX_PAGES}, YelpDelay={config.YELP_REQUEST_DELAY_SECONDS}s, "
        f"FSQDelay={config.FSQ_REQUEST_DELAY_SECONDS}s, "
        f"QUICK_MAX_TILES={config.QUICK_MAX_TILES}, QUICK_MAX_YELP_CATS={config.QUICK_MAX_YELP_CATS}, "
        f"QUICK_MAX_FSQ_QUERIES={config.QUICK_MAX_FSQ_QUERIES}"
    )

    test_foursquare_auth()

    # Yelp
    yelp_vendors = fetch_yelp_data_tiled()
    tmp_yelp = os.path.join(outputs_dir, "yelp_partial.json")
    with open(tmp_yelp, "w", encoding="utf-8") as f:
        json.dump(yelp_vendors, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote partial Yelp vendors to {tmp_yelp}")

    # FSQ
    fsq_vendors = fetch_foursquare_data_tiled()
    tmp_fsq = os.path.join(outputs_dir, "fsq_partial.json")
    with open(tmp_fsq, "w", encoding="utf-8") as f:
        json.dump(fsq_vendors, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote partial FSQ vendors to {tmp_fsq}")

    # Merge
    all_vendors = yelp_vendors + fsq_vendors
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_vendors, f, indent=2, ensure_ascii=False)

    elapsed = (datetime.utcnow() - START_TS).total_seconds()
    logger.info(
        f"Done. Total vendors={len(all_vendors)} (Yelp={len(yelp_vendors)}, FSQ={len(fsq_vendors)}). "
        f"Requests={REQUESTS_MADE}, Elapsed={elapsed:.1f}s, Rate={_rate(elapsed):.2f} req/s"
    )
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()