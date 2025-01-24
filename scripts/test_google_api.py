import json
import requests
from dotenv import load_dotenv
import os

# Force reload of the .env file
load_dotenv(override=True)

# # Load environment variables from .env
# load_dotenv()

# Fetch Google Maps API key from environment variables
GOOGLE_API_KEY = os.getenv("google_api_key")  # Updated to match your .env key
#LOCATION = "Sicily"
LOCATION = "37.6,13.4"  # Latitude and longitude for Sicily
RADIUS = 1000000  # 100 km radius
BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

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
        #     for place in data.get("results", []):
        #         print(f"Name: {place['name']}, Address: {place.get('vicinity', 'N/A')}")
                    # Pretty-print the JSON response
            pretty_data = json.dumps(data, indent=4)
            print(pretty_data)
            
            # Save the JSON response to a file
            with open(f'response_{keyword}.json', 'w') as json_file:
                json.dump(data, json_file, indent=4)
            
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

    # print('\n')
    # print(place)
