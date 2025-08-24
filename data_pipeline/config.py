"""
This script contains centralized configuration settings for the application.
It includes API rate limits, database paths, and geographical parameters specific to Sicily.
These configurations are used throughout the application to ensure consistency and maintainability.
"""

# config.py
import os

# Sicily bounding box (approx: south, west, north, east)
SICILY_BBOX = "36.65,12.42,38.22,15.65"

# Major cities for targeted queries
SICILY_CITIES = ["Palermo"]

# SICILY_CITIES = ["Palermo", "Catania", "Syracuse", "Messina", 
#                  "Taormina", "Trapani", "Agrigento", "Enna", "Caltanissetta", "Ragusa"]

# Wedding service categories (for Yelp/Foursquare/OSM tags)
WEDDING_CATEGORIES = [
    "wedding_planning", "photographers", "caterers", "event_venues", "florist"
]

# # OSM tags for wedding-related queries
# OSM_TAGS = {
#     "amenity": ["event_venue", "community_centre"],
#     "shop": ["florist", "caterer"],
#     "wedding": True  # Keyword search
# }

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

# OSM_TAGS = {
#     "shop": [
#         "florist", "jewelry", "caterer", "beauty", "hairdresser", 
#         "wedding", "pastry", "tailor", "travel_agency", "wine"
#     ],
#     "amenity": [
#         "restaurant", "cafe", "bar", "pub", "place_of_worship",
#         "community_centre", "social_club"
#     ],
#     "tourism": [
#         "hotel", "guest_house", "apartment", "hostel"
#     ],
#     "craft": [
#         "photographer", "caterer", "planner", "dressmaker"
#     ]
# }

# Database URI (override in .env if needed)
DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///vendors.db")