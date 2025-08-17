"""
This script serves as the main entry point for the data pipeline. It orchestrates the entire process
of fetching vendor data from various APIs (OSM, Yelp, Foursquare), enriching the data with geocoding
information, and storing the processed data in the database. The pipeline ensures that all steps are
executed sequentially, and the final output is stored in the `vendors.db` SQLite database.

Steps:
1. Fetch vendor data from OpenStreetMap (OSM) using Overpass API.
2. Fetch vendor data from Yelp and Foursquare APIs.
3. Enrich the fetched data with geocoding information using OpenCage API.
4. Process and store the enriched data in the database, ensuring deduplication.

Output:
- The processed data is stored in `vendors.db`.
- Intermediate JSON files are saved in the `outputs` directory.
"""

# data_pipeline/main.py (Run all steps)
import api_fetch_osm
import api_fetch_yelp_foursquare
import geocode_opencage
import data_processor

if __name__ == "__main__":
    api_fetch_osm.fetch_osm_data()
    api_fetch_yelp_foursquare.main()
    geocode_opencage.enrich_locations("outputs/osm_vendors.json", "outputs/osm_enriched.json")
    geocode_opencage.enrich_locations("outputs/yelp_fsq_vendors.json", "outputs/yelp_fsq_enriched.json")
    data_processor.process_and_store(["outputs/osm_enriched.json", "outputs/yelp_fsq_enriched.json"])
    print("Pipeline complete! vendors.db populated.")