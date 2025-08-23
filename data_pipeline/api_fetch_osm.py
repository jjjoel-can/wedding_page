# # api_fetch_osm.py
# import overpy
# import json
# import config  # Import Sicily config
# from dotenv import load_dotenv
# load_dotenv()

# # Optional: import osmnx as ox  # For advanced fetches [osmnx.readthedocs.io]

# api = overpy.Overpass()

# def fetch_osm_data():
#     vendors = []
#     # query = f"""
#     # [out:json];
#     # area["name"="Sicily"]->.searchArea;
#     # (node["shop"~"florist|caterer"](area.searchArea);
#     #  way["amenity"~"event_venue"](area.searchArea););
#     # out body;
#     # """
#     query = f"""
#     [out:json];
#     area["name"="Sicily"]->.searchArea;
#     node(area.searchArea);
#     out body;
#     """
#     # Alternatively, use bbox: node({config.SICILY_BBOX.split(',')})
#     result = api.query(query)
    
#     # Inspect nodes
#     print("Nodes:")
#     for node in result.nodes:
#         print(f"ID: {node.id}, Latitude: {node.lat}, Longitude: {node.lon}, Tags: {node.tags}")

#     # Inspect ways
#     print("\nWays:")
#     for way in result.ways:
#         print(f"ID: {way.id}, Nodes: {way.nodes}, Tags: {way.tags}")

#     # Inspect relations
#     print("\nRelations:")
#     for relation in result.relations:
#         print(f"ID: {relation.id}, Members: {relation.members}, Tags: {relation.tags}")
    
#     for way in result.ways:
#         print(f"Processing way: {way.id}")
#         tags = way.tags
#         vendor = {
#             "name": tags.get("name", "Unknown"),
#             "service_type": tags.get("shop") or tags.get("amenity") or "unknown",
#             "address": tags.get("addr:street", ""),
#             "city": tags.get("addr:city", ""),
#             "contact": tags.get("phone", ""),
#             "website": tags.get("website", "")
#         }
#         vendors.append(vendor)
    
#     # Optional: Use OSMnx for buildings/networks
#     # G = ox.features_from_bbox(*map(float, config.SICILY_BBOX.split(',')), tags={"building": True})
    
#     with open("osm_vendors.json", "w") as f:
#         json.dump(vendors, f)
#     print(f"Fetched {len(vendors)} OSM vendors for Sicily.")

# if __name__ == "__main__":
#     fetch_osm_data()

# api_fetch_osm.py

# data_pipeline/api_fetch_osm.py
import overpy
import json
import os
import config
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure the output directory exists
os.makedirs("outputs", exist_ok=True)
OUTPUT_FILE = "outputs/osm_vendors.json"

WEDDING_TAGS = config.OSM_TAGS  # Use the tags defined in config.py


def build_overpass_query():
    """Builds the Overpass QL query string from the WEDDING_TAGS dictionary."""
    query_parts = []
    for key, values in WEDDING_TAGS.items():
        # Creates a regex string like "florist|jewelry|caterer"
        regex_values = "|".join(values)
        # Adds lines for both nodes and ways to the query
        query_parts.append(f'node["{key}"~"{regex_values}"](area.searchArea);')
        query_parts.append(f'way["{key}"~"{regex_values}"](area.searchArea);')

    # Join all the individual query parts into a single block
    full_query_block = "\n  ".join(query_parts)

    query = f"""
    [out:json][timeout:120];
    area["name"="Sicily"]->.searchArea;
    (
      {full_query_block}
    );
    out body;
    >;
    out skel qt;
    """
    return query


def _extract_vendor_data(element, osm_type):
    """Helper function to extract common data from a node or way."""
    tags = element.tags
    vendor = {
        "osm_id": element.id,
        "osm_type": osm_type,
        "name": tags.get("name", "N/A"),
        "service_type": (
            tags.get("shop") or
            tags.get("amenity") or
            tags.get("tourism") or
            tags.get("craft") or
            "unknown"
        ),
        "lat": None,
        "lon": None,
        "address": tags.get("addr:full") or f"{tags.get('addr:street', '')} {tags.get('addr:housenumber', '')}".strip(),
        "city": tags.get("addr:city", ""),
        "postcode": tags.get("addr:postcode", ""),
        "contact": tags.get("phone") or tags.get("contact:phone", ""),
        "website": tags.get("website") or tags.get("contact:website", ""),
        "source": "osm"
    }
    
    # Get coordinates based on element type
    if osm_type == 'node':
        vendor["lat"] = float(element.lat)
        vendor["lon"] = float(element.lon)
    elif osm_type == 'way':
        vendor["lat"] = float(element.center_lat)
        vendor["lon"] = float(element.center_lon)

    return vendor


def fetch_osm_data():
    """
    Fetches wedding-related vendor data for Sicily from the Overpass API
    and saves it to a JSON file. 
    """
    api = overpy.Overpass()
    query = build_overpass_query()

    # Print the query for debugging purposes
    print("Overpass API Query:")
    print(query)
    
    print("Executing Overpass API query for Sicily... (This may take a minute)")
    try:
        result = api.query(query)
    except Exception as e:
        print(f"An error occurred while querying the Overpass API: {e}")
        return

    vendors = []
    processed_ids = set() # To avoid duplicates if an element is tagged multiple times

    # Process all NODES from the result
    for node in result.nodes:
        if node.id not in processed_ids:
            vendors.append(_extract_vendor_data(node, 'node'))
            processed_ids.add(node.id)

    # Process all WAYS from the result
    for way in result.ways:
        if way.id not in processed_ids:
            vendors.append(_extract_vendor_data(way, 'way'))
            processed_ids.add(way.id)

    # Save the data to the specified output file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(vendors, f, indent=2, ensure_ascii=False)
        
    print(f"Success! Fetched {len(vendors)} potential vendors from OpenStreetMap.")
    print(f"Data saved to `{OUTPUT_FILE}`.")

# def main():
#     """Main function to run the OSM data fetch."""

#     # load_dotenv() # Load environment variables from .env file
#     # os.makedirs("outputs", exist_ok=True)  # Ensure the output directory exists
#     # OUTPUT_FILE = "outputs/osm_vendors.json"
#     # WEDDING_TAGS = config.OSM_TAGS  # Use the tags defined in config.py

#     #fetch_osm_data()

#     # build overpass query
#     query = build_overpass_query()
#     print("Overpass Query:") # debugging
#     print(query)

#     print('calling api')
#     api = overpy.Overpass()

#     try:
#         result = api.query(query)
#     except Exception as e:
#         print(f"An error occurred while querying the Overpass API: {e}")
#     else:
#         print("Query executed successfully.")
#         return

#     print(result)

#     # If the query was successful, process the results
#     # nodes and ways

#     #vendors = []

#     for node in result.nodes:
#         print(node.id, node.lat, node.lon, node.tags)


#     return


if __name__ == "__main__":

    # build overpass query
    query = build_overpass_query()
    print("Overpass Query:") # debugging
    print(query)

    print('calling api')
    api = overpy.Overpass()

    try:
        result = api.query(query)
    except Exception as e:
        print(f"An error occurred while querying the Overpass API: {e}")
    else:
        print("Query executed successfully.")

    print(result)

    # If the query was successful, process the results
    # nodes and ways

    #vendors = []

    print('*' * 50)
    print('Nodes:')

    for node in result.nodes:
        print(node.id, node.lat, node.lon, node.tags)

    print('*' * 50)
    print('Ways:')

    for way in result.ways:
        print(way.id, way.center_lat, way.center_lon, way.tags)