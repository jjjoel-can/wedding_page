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
# import api_fetch_osm
# import api_fetch_yelp_foursquare
# import geocode_opencage
# import data_processor

# if __name__ == "__main__":
#     api_fetch_osm.fetch_osm_data()
#     api_fetch_yelp_foursquare.main()
#     geocode_opencage.enrich_locations("outputs/osm_vendors.json", "outputs/osm_enriched.json")
#     #geocode_opencage.enrich_locations("outputs/yelp_fsq_vendors.json", "outputs/yelp_fsq_enriched.json")
#     data_processor.process_and_store(["outputs/osm_enriched.json", "outputs/yelp_fsq_enriched.json"])
#     print("Pipeline complete! vendors.db populated.")

# data_pipeline/main.py (Run all steps with logging)
import os
import time
import logging

import api_fetch_osm
import api_fetch_yelp_foursquare
import geocode_opencage
import data_processor

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _abs_path(*parts) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def _run_step(name, func, *args, **kwargs) -> bool:
    logger.info(f"Starting: {name}")
    t0 = time.perf_counter()
    try:
        func(*args, **kwargs)
        dt = time.perf_counter() - t0
        logger.info(f"Finished: {name} in {dt:.2f}s")
        return True
    except Exception:
        dt = time.perf_counter() - t0
        logger.exception(f"Failed: {name} after {dt:.2f}s")
        return False


def main():
    logger.info("Pipeline started.")

    # Paths
    osm_raw = _abs_path("outputs", "osm_vendors.json")
    osm_enriched = _abs_path("outputs", "osm_enriched.json")
    yelp_fsq_raw = _abs_path("outputs", "yelp_fsq_vendors.json")
    yelp_fsq_enriched = _abs_path("outputs", "yelp_fsq_enriched.json")

    # Steps
    _run_step("Fetch OSM vendors", api_fetch_osm.fetch_osm_data)
    _run_step("Fetch Yelp/Foursquare vendors", api_fetch_yelp_foursquare.main)

    # Enrich OSM vendors (reverse geocode preferred)
    if os.path.exists(osm_raw):
        _run_step(
            "Enrich OSM vendors with OpenCage",
            geocode_opencage.enrich_locations,
            osm_raw,
            osm_enriched,
        )
    else:
        logger.warning(f"OSM input not found at {osm_raw}; skipping OSM enrichment.")

    # Optionally enrich Yelp/FSQ (uncomment if needed)
    # if os.path.exists(yelp_fsq_raw):
    #     _run_step(
    #         "Enrich Yelp/FSQ vendors with OpenCage",
    #         geocode_opencage.enrich_locations,
    #         yelp_fsq_raw,
    #         yelp_fsq_enriched,
    #     )
    # else:
    #     logger.warning(f"Yelp/FSQ input not found at {yelp_fsq_raw}; skipping Yelp/FSQ enrichment.")

    # Collect enriched files to process
    inputs_to_process = []
    if os.path.exists(osm_enriched):
        inputs_to_process.append(osm_enriched)
    if os.path.exists(yelp_fsq_enriched):
        inputs_to_process.append(yelp_fsq_enriched)

    if not inputs_to_process:
        logger.error("No enriched files found to process. Aborting database load.")
        return

    _run_step(
        "Process and store vendors into database",
        data_processor.process_and_store,
        inputs_to_process,
    )

    logger.info("Pipeline complete! vendors.db populated.")


if __name__ == "__main__":
    main()