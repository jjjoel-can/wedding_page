"""
This script contains centralized configuration settings for the application.
It includes API rate limits, database paths, and geographical parameters specific to Sicily.
These configurations are used throughout the application to ensure consistency and maintainability.
"""

# config.py
# Centralized configuration for tiling, pacing, retries, pagination,
# quick-mode limits, and search taxonomies.

import os
from math import cos, radians
import math
from typing import Tuple


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except Exception:
        return default

def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except Exception:
        return default

def _env_str(name: str, default: str) -> str:
    return os.getenv(name, default)

# Geography
# Sicily bbox (south, west, north, east)
SICILY_BBOX = _env_str("SICILY_BBOX", "36.65,12.42,38.22,15.65")

# Tiling
TILE_RADIUS_METERS = _env_int("TILE_RADIUS_METERS", 35000)
TILE_STEP_FRACTION = _env_float("TILE_STEP_FRACTION", 0.9)

# Requests pacing & retries
YELP_REQUEST_DELAY_SECONDS = _env_float("YELP_REQUEST_DELAY_SECONDS", 1.8)
FSQ_REQUEST_DELAY_SECONDS = _env_float("FSQ_REQUEST_DELAY_SECONDS", 0.4)

MAX_RETRIES = _env_int("MAX_RETRIES", 3)
BACKOFF_BASE_SECONDS = _env_float("BACKOFF_BASE_SECONDS", 1.2)

# Yelp rate-limit handling
YELP_429_COOLDOWN_SECONDS = _env_int("YELP_429_COOLDOWN_SECONDS", 60)
YELP_MAX_CONSECUTIVE_429 = _env_int("YELP_MAX_CONSECUTIVE_429", 6)

# Pagination caps
YELP_LIMIT = 50
YELP_MAX_OFFSET = 1000  # Yelp hard cap
FSQ_LIMIT = 50
FSQ_MAX_PAGES = _env_int("FSQ_MAX_PAGES", 3)  # keep small for speed; increase for full runs

# Quick mode (limit scope for testing; 0 means “no limit”)
QUICK_MAX_TILES = _env_int("QUICK_MAX_TILES", 0)
QUICK_MAX_YELP_CATS = _env_int("QUICK_MAX_YELP_CATS", 0)
QUICK_MAX_FSQ_QUERIES = _env_int("QUICK_MAX_FSQ_QUERIES", 0)

# Search taxonomies
# Yelp Fusion category aliases
YELP_CATEGORIES = [
    "wedding_planning",
    "photographers",
    "videographers",
    "florists",
    "bridal",
    "venues",       # Venues & Event Spaces
    "caterers",
    "hair",
    "barbers",
    "makeupartists",
]

# Foursquare keyword queries (EN/IT to capture local phrasing)
FSQ_QUERIES = [
    "wedding planner",
    "wedding planning",
    "matrimonio",
    "fotografo",
    "photographer",
    "videographer",
    "florist",
    "fioraio",
    "bridal",
    "abiti da sposa",
    "venue",
    "event venue",
    "location matrimoni",
    "catering",
    "caterer",
    "hairdresser",
    "parrucchiere",
    "barber",
    "barbiere",
    "make up",
    "trucco sposa",
]

# Geo helpers (shared)
def sicily_bbox_tuple() -> Tuple[float, float, float, float]:
    s, w, n, e = map(float, SICILY_BBOX.split(","))
    return s, w, n, e

def degree_step_lat(radius_m: float) -> float:
    # ~ meters per degree latitude
    return radius_m / 111_320.0

def degree_step_lon(radius_m: float, lat_deg: float) -> float:
    # ~ meters per degree longitude adjusted by cos(lat)
    return radius_m / (111_320.0 * max(0.15, math.cos(math.radians(lat_deg))))

# # Sicily bounding box (approx: south, west, north, east)
# SICILY_BBOX = "36.65,12.42,38.22,15.65"

# Major cities for targeted queries
SICILY_CITIES = ["Palermo"]

# SICILY_CITIES = ["Palermo", "Catania", "Syracuse", "Messina", 
#                  "Taormina", "Trapani", "Agrigento", "Enna", "Caltanissetta", "Ragusa"]

# Wedding service categories (for Yelp/Foursquare/OSM tags)
WEDDING_CATEGORIES = [
    "wedding_planning", "photographers", "caterers", "event_venues", "florist"
]

# # Sicily bounding box (south, west, north, east)
# SICILY_BBOX = "36.65,12.42,38.22,15.65"

# Tiling settings for API scans
# Radius in meters for each tile query; Yelp max radius ~40000
TILE_RADIUS_METERS = int(os.getenv("TILE_RADIUS_METERS", "15000"))

# Step fraction between tile centers relative to radius (0.8 -> 20% overlap)
TILE_STEP_FRACTION = float(os.getenv("TILE_STEP_FRACTION", "0.8"))

# Request pacing and retries
REQUEST_DELAY_SECONDS = float(os.getenv("REQUEST_DELAY_SECONDS", "0.5"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
BACKOFF_BASE_SECONDS = float(os.getenv("BACKOFF_BASE_SECONDS", "1.2"))

# Pagination caps
YELP_LIMIT = 50
YELP_MAX_OFFSET = 1000  # hard Yelp cap
FSQ_LIMIT = 50
FSQ_MAX_PAGES = int(os.getenv("FSQ_MAX_PAGES", "20"))

# Tight “wedding value chain” categories
# Yelp Fusion category aliases: https://docs.developer.yelp.com/docs/fusion-api#categories
YELP_CATEGORIES = [
    "wedding_planning",
    "photographers",
    "videographers",
    "florists",
    "bridal",
    "venues",          # Venues & Event Spaces
    "caterers",
    "hair",
    "barbers",
    "makeupartists",
    # Optionally add: "eventplanning", "partyandeventplanning"
]

# Foursquare v3 search will use keyword queries per tile.
# We keep focused English/Italian terms commonly used in listings.
FSQ_QUERIES = [
    "wedding planner",
    "wedding planning",
    "matrimonio",
    "fotografo",
    "photographer",
    "videographer",
    "florist",
    "fioraio",
    "bridal",
    "abiti da sposa",
    "venue",
    "event venue",
    "location matrimoni",
    "catering",
    "caterer",
    "hairdresser",
    "parrucchiere",
    "barber",
    "barbiere",
    "make up",
    "trucco sposa",
]

# # Database URI (override in .env if needed)
# DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///vendors.db")


def sicily_bbox_tuple():
    s, w, n, e = map(float, SICILY_BBOX.split(","))
    return s, w, n, e


def degree_step_lat(radius_m):
    # Rough meters per degree latitude ~111_320
    return radius_m / 111_320.0


def degree_step_lon(radius_m, lat_deg):
    # Meters per degree longitude ~111_320 * cos(lat)
    return radius_m / (111_320.0 * max(0.15, cos(radians(lat_deg))))

# Note: OSM coverage varies; we include direct wedding tags and supportive categories.
OSM_TAGS = [
    ('shop', 'wedding'),         # bridal shops
    ('shop', 'florist'),         # florists
    ('craft', 'photographer'),   # photographers (service)
    ('shop', 'photo'),           # photo shops (sometimes also photographers)
    ('shop', 'hairdresser'),     # hair stylist
    ('amenity', 'beauty_salon'), # makeup/beauty
    # Venues – sparsely tagged but worth checking
    ('amenity', 'community_centre'),
    ('amenity', 'conference_centre'),
    ('amenity', 'banquet_hall'),
    ('amenity', 'events_venue'),
    # Caterers – not very standardized; 'craft=caterer' exists sometimes
    ('craft', 'caterer'),
]

# Database URI (override in .env if needed)
DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///vendors.db")