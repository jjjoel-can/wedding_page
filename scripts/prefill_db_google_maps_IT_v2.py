# import sys
# import os
# import json
# from dotenv import load_dotenv
# import requests
# import time

# # Add the parent directory to the system path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# from app.app import db, create_app
# from app.models import Vendor

# # Load environment variables
# load_dotenv(override=True)
# app = create_app()

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
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# List of keywords
keywords = ["wedding", "venue", "bridal", "event planner", "photographer", "bride", "wedding planner"]

# List of major Italian cities
italian_cities = [
    "Rome, Italy",
    # Add more cities as needed
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

def get_place_details(place_id):
    """Fetch detailed information for a place using its place_id."""
    params = {
        "key": GOOGLE_API_KEY,
        "place_id": place_id,
        "fields": "name,website,formatted_address,international_phone_number,opening_hours,photos"
    }
    response = requests.get(DETAILS_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            return data.get("result", {})
    print(f"Failed to fetch details for place_id: {place_id}")
    return {}

def prefill_database(data, keyword, country):
    """Add data to the database, including the country."""
    if data:
        for place in data.get("results", []):
            # Fetch detailed information using the place_id
            place_id = place.get('place_id')
            if not place_id:
                print(f"Skipping place '{place.get('name', 'N/A')}' due to missing place_id.")
                continue

            details = get_place_details(place_id)
            if not details:
                continue

            # Extract relevant fields from the detailed response
            name = details.get('name', 'N/A')
            address = details.get('formatted_address', 'N/A')  # Full address
            city = address.split(',')[-1].strip() if address else 'N/A'  # Extract city from address
            contact = details.get('international_phone_number', 'N/A')  # Phone number
            hours = details.get('opening_hours', {}).get('weekday_text', 'N/A')  # Operating hours
            photos = details.get('photos', [])
            picture_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photos[0]['photo_reference']}&key={GOOGLE_API_KEY}" if photos else 'N/A'  # First photo URL
            website = details.get('website', 'N/A')  # Website URL

            # Check if the vendor already exists in the database
            existing_vendor = Vendor.query.filter_by(name=name, address=address).first()
            if existing_vendor:
                print(f"Vendor '{name}' already exists in the database.")
                continue

            # Create a new Vendor object
            vendor = Vendor(
                name=name,
                country=country,  # Add the country field
                service_type=keyword,
                address=address,  # Use full address
                city=city,  # Extract city from address
                contact=contact,  # Use phone number
                hours=str(hours) if hours else 'N/A',  # Convert list to string
                picture_url=picture_url,  # Use photo URL
                website=website  # Add website field
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
                try:
                    data = get_google_maps_data(params)
                    if data:
                        prefill_database(data, keyword, country='Italy')
                    else:
                        print(f"No data found for keyword '{keyword}' in {city}.")
                except Exception as e:
                    print(f"Error processing {city} for keyword '{keyword}': {e}")
        else:
            print(f"Skipping {city} due to geocoding failure.")

if __name__ == "__main__":
    with app.app_context():
        main()