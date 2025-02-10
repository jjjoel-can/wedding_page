import sys
import os
import json
from dotenv import load_dotenv
import requests
import time


# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#from app import db
from app.app import db, create_app
from app.models import Vendor
import requests


# Load environment variables from .env file
# Force reload of the .env file
load_dotenv(override=True)
app = create_app()


# Fetch Google Maps API key from environment variables
GOOGLE_API_KEY = os.getenv("google_api_key")
RADIUS = 50000  # 50 km radius (adjust as needed)
BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# List of keywords
keywords = ["wedding", "venue", "bridal", "event planner", "photographer", "bride", "wedding planner"]

# List of major Italian cities
italian_cities = [
    "Rome, Italy",
    "Milan, Italy",
    "Naples, Italy",
    "Turin, Italy",
    "Palermo, Italy",
    "Genoa, Italy",
    "Bologna, Italy",
    "Florence, Italy",
    "Venice, Italy",
    "Verona, Italy",
    "Bari, Italy",
    "Catania, Italy",
    "Messina, Italy",
    "Padua, Italy",
    "Trieste, Italy"
]

def geocode_city(city_name, api_key):
    """Fetch latitude and longitude for a city using Google Geocoding API."""
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={api_key}"
    response = requests.get(geocode_url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    print(f"Failed to geocode city: {city_name}")
    return None, None

def get_google_maps_data(params):
    """Fetch data from Google Places API."""
    all_results = []
    while True:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            all_results.extend(data.get("results", []))
            if "next_page_token" in data:
                params["pagetoken"] = data["next_page_token"]
                time.sleep(2)  # Wait for the next page token to become valid
            else:
                break
        else:
            print(f"Failed to fetch data: {response.status_code}")
            break
    return {"results": all_results}

def prefill_database(data, keyword, country):
    """Add data to the database, including the country."""
    if data:
        for place in data.get("results", []):
            vendor = Vendor(
                name=place['name'],
                country=country,  # Add the country field
                service_type=keyword,
                address=place.get('vicinity', 'N/A'),
                city=place.get('vicinity', 'N/A'),  # You can refine this later
                contact=place.get('vicinity', 'N/A'),  # Placeholder for contact
                hours=place.get('vicinity', 'N/A'),  # Placeholder for hours
                picture_url=place.get('vicinity', 'N/A')  # Placeholder for picture URL
            )
            db.session.add(vendor)
            db.session.commit()
            print(f"Vendor '{vendor.name}' added to the database in {country}.")

def main():
    for city in italian_cities:
        lat, lng = geocode_city(city, GOOGLE_API_KEY)
        if lat and lng:
            location = f"{lat},{lng}"
            print(f"Searching for wedding services in {city}...")
            for keyword in keywords:
                params = {
                    "key": GOOGLE_API_KEY,
                    "location": location,
                    "radius": RADIUS,
                    "keyword": keyword
                }
                data = get_google_maps_data(params)
                prefill_database(data, keyword, country='Italy') # Add the country field
        else:
            print(f"Skipping {city} due to geocoding failure.")

if __name__ == "__main__":
    with app.app_context():
        main()