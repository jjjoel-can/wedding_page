"""
This script processes vendor data from JSON input files and stores it in the database.
It uses SQLAlchemy to interact with the database and ensures that duplicate entries
are removed before storing the data. The script assumes the input files contain vendor
information in JSON format and that the database schema is already defined in models.py.
"""

# data_processor.py
import json
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
#from models import db, Vendor  # Assume models.py has db and Vendor

import config
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import db, Vendor
load_dotenv()

engine = create_engine(config.DATABASE_URI)
Session = sessionmaker(bind=engine)
db.Model.metadata.create_all(engine)  # Init tables if needed

def process_and_store(input_files):
    all_vendors = []
    for file in input_files:
        with open(file, "r") as f:
            all_vendors.extend(json.load(f))
    
    # Deduplicate by name + address
    unique_vendors = {}
    for v in all_vendors:
        key = (v["name"].lower(), v.get("address", "").lower())
        if key not in unique_vendors:
            unique_vendors[key] = v
    
    session = Session()
    for v in unique_vendors.values():
        # Normalize (e.g., add defaults)
        v["country"] = v.get("country", "Italy")
        v["price_range"] = v.get("price_range", "Unknown")  # Placeholder; enrich later if needed
        
        # TODO: possibly wrong tags mapping from source to DB fields
        vendor = Vendor(
            name=v["name"],
            country=v["country"],
            service_type=v["service_type"],
            price_range=v["price_range"],
            address=v.get("address"),
            city=v.get("city"),
            contact=v.get("contact"),
            hours=v.get("hours"),
            picture_url=v.get("picture_url"),
            website=v.get("website"),
            # Social fields: Placeholder; scrape/enrich in future phases
        )
        try:
            session.add(vendor)
            session.commit()
        except exc.IntegrityError:
            session.rollback()  # Skip duplicates
    
    session.close()
    print(f"Stored {len(unique_vendors)} unique vendors in DB.")

if __name__ == "__main__":

    #base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    osm_enriched = os.path.join(out_dir, "osm_enriched.json")
    yelp_fsq_enriched = os.path.join(out_dir, "yelp_fsq_enriched.json")
    process_and_store([osm_enriched, yelp_fsq_enriched])
