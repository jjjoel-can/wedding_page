'''
- Created V1.0 on Jan 25
- Prefill database with relevant data using google places api
'''

import sys
import os
from dotenv import load_dotenv
import requests

# from app import db
# from app.models import Vendor

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from models import Vendor

app = create_app()

with app.app_context():
    # Drop and recreate tables for a clean slate (optional)
    db.drop_all()
    db.create_all()

    # Sample data
    sample_vendors = [
        Vendor(name="Elegant Weddings", service_type="Planner", price_range="$$$"),
        Vendor(name="Golden Rings Catering", service_type="Caterer", price_range="$$"),
        Vendor(name="Bella Vista Venue", service_type="Venue", price_range="$$$$")
    ]

    # Add data to the database
    db.session.add_all(sample_vendors)
    db.session.commit()

    print("Database has been prefilled with sample vendors.")

load_dotenv()

API_KEY = os.getenv("google_api_key")
BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

def fetch_vendors(city, radius=50000, keyword="wedding"):
    # Set latitude and longitude for the city (e.g., Palermo, Sicily)
    location_map = {
        "Palermo": "38.1157,13.3615",
        "Catania": "37.5079,15.0830"
        # Add more cities as needed
    }
    location = location_map.get(city, None)
    if not location:
        print(f"City '{city}' not supported.")
        return []

    params = {
        "key": API_KEY,
        "location": location,
        "radius": radius,
        "keyword": keyword
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json().get("results", [])
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return []

def prefill_database(city):
    vendors = fetch_vendors(city)
    if not vendors:
        print(f"No data found for {city}")
        return

    for vendor in vendors:
        name = vendor.get("name")
        address = vendor.get("vicinity")
        # Create or update database entry
        new_vendor = Vendor(
            name=name,
            service_type="wedding",  # This can be adjusted based on your keyword
            price_range=None,  # Google API doesn't provide price_range directly
            address=address,
            city=city
        )
        db.session.add(new_vendor)

    db.session.commit()
    print(f"Database prefilled with vendors from {city}.")

if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        db.create_all()  # Ensure tables are created
        prefill_database("Palermo")  # Example: Prefill data for Palermo
