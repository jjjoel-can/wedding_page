import sys
import os
import json
from dotenv import load_dotenv


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

# throws an erro for some reason
# with app.app_context():
#     # Drop and recreate tables for a clean slate (optional)
#     db.drop_all()
#     db.create_all()

# Fetch Google Maps API key from environment variables
GOOGLE_API_KEY = os.getenv("google_api_key")  # Updated to match your .env key
#LOCATION = "Sicily"
LOCATION = "37.6,13.4"  # Latitude and longitude for Sicily
RADIUS = 1000000  # 100 km radius
BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# list of keywords
keywords = ["wedding", "venue", "bridal", "event planner", "photographer", "bride", "wedding planer"]

for keyword in keywords:
    params = {
        "key": GOOGLE_API_KEY,
        "location": LOCATION,
        "radius": RADIUS,
        "keyword": keyword
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        print(f"Results for keyword '{keyword}':")
        if data["status"] == "ZERO_RESULTS":
            print("No results found.")
        else:
            pretty_data = json.dumps(data, indent=4)
            print(pretty_data)
            
            # forget about saving to folder
            # # Save the JSON response to a file in the current folder
            # file_name = f'response_{keyword.replace(" ", "_")}.json'
            # file_path = os.path.join(current_dir, file_name)
            # with open(file_path, 'w') as json_file:
            #     json.dump(data, json_file, indent=4)
            # print(f"Response saved to {file_path}")
            
            for place in data.get("results", []):
                print(f"Name: {place['name']}")
                print(f"Address: {place.get('vicinity', 'N/A')}")
                print(f"Rating: {place.get('rating', 'N/A')}")
                print(f"User Ratings Total: {place.get('user_ratings_total', 'N/A')}")
                print(f"Types: {', '.join(place.get('types', []))}")
                print(f"Business Status: {place.get('business_status', 'N/A')}")
                print(f"Place ID: {place.get('place_id', 'N/A')}")
                print(f"Location: {place['geometry']['location']['lat']}, {place['geometry']['location']['lng']}")
                print("-" * 40)
    else:
        print(f"Failed to fetch data for keyword '{keyword}'")