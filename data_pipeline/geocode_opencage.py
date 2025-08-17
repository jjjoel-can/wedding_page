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
from opencage.geocoder import OpenCageGeocode
import json
import os
from dotenv import load_dotenv

load_dotenv()

geocoder = OpenCageGeocode(os.getenv("open_cage_api_key"))


def enrich_locations(input_file, output_file):
    try:
        with open(input_file, "r") as f:
            vendors = json.load(f)
    except FileNotFoundError:
        print(f"Warning: Input file '{input_file}' not found. Skipping enrichment.")
        return
    
    for vendor in vendors:
        if not vendor.get("address") or not vendor.get("city"):
            query = vendor.get("name") + ", Sicily, Italy"
            result = geocoder.geocode(query)
            if result:
                components = result[0]["components"]
                vendor["address"] = result[0]["formatted"]
                vendor["city"] = components.get("city", "Unknown")
                vendor["country"] = components.get("country", "Italy")
    
    try:
        with open(output_file, "w") as f:
            json.dump(vendors, f)
        print(f"Enriched {len(vendors)} vendors with OpenCage.")
    except FileNotFoundError:
        print(f"Warning: Output file '{output_file}' could not be created.")

if __name__ == "__main__":
    # Run on OSM and Yelp/FSQ outputs
    enrich_locations("osm_vendors.json", "osm_enriched.json")
    enrich_locations("yelp_fsq_vendors.json", "yelp_fsq_enriched.json")
