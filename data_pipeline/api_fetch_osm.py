# api_fetch_osm.py
import overpy
import json
import config  # Import Sicily config
from dotenv import load_dotenv
load_dotenv()

# Optional: import osmnx as ox  # For advanced fetches [osmnx.readthedocs.io]

api = overpy.Overpass()

def fetch_osm_data():
    vendors = []
    # query = f"""
    # [out:json];
    # area["name"="Sicily"]->.searchArea;
    # (node["shop"~"florist|caterer"](area.searchArea);
    #  way["amenity"~"event_venue"](area.searchArea););
    # out body;
    # """
    query = f"""
    [out:json];
    area["name"="Sicily"]->.searchArea;
    node(area.searchArea);
    out body;
    """
    # Alternatively, use bbox: node({config.SICILY_BBOX.split(',')})
    result = api.query(query)
    
    # Inspect nodes
    print("Nodes:")
    for node in result.nodes:
        print(f"ID: {node.id}, Latitude: {node.lat}, Longitude: {node.lon}, Tags: {node.tags}")

    # Inspect ways
    print("\nWays:")
    for way in result.ways:
        print(f"ID: {way.id}, Nodes: {way.nodes}, Tags: {way.tags}")

    # Inspect relations
    print("\nRelations:")
    for relation in result.relations:
        print(f"ID: {relation.id}, Members: {relation.members}, Tags: {relation.tags}")
    
    for way in result.ways:
        print(f"Processing way: {way.id}")
        tags = way.tags
        vendor = {
            "name": tags.get("name", "Unknown"),
            "service_type": tags.get("shop") or tags.get("amenity") or "unknown",
            "address": tags.get("addr:street", ""),
            "city": tags.get("addr:city", ""),
            "contact": tags.get("phone", ""),
            "website": tags.get("website", "")
        }
        vendors.append(vendor)
    
    # Optional: Use OSMnx for buildings/networks
    # G = ox.features_from_bbox(*map(float, config.SICILY_BBOX.split(',')), tags={"building": True})
    
    with open("osm_vendors.json", "w") as f:
        json.dump(vendors, f)
    print(f"Fetched {len(vendors)} OSM vendors for Sicily.")

if __name__ == "__main__":
    fetch_osm_data()