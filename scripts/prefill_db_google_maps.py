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



def get_google_maps_data(params):
    '''call google maps api and return data 
    in a way that is usable for database'''

    # get response from google maps api
    response = requests.get(BASE_URL, params=params)

    # only proceed if the response is successful
    if response.status_code == 200:
        data = response.json()
        print(f"Results for keyword '{keyword}':")
        # check if results are empty
        if data["status"] == "ZERO_RESULTS":
            print("No results found.")
            return None
        # print results in a pretty format
        #else:
            #pretty_data = json.dumps(data, indent=4)
            #print(pretty_data)
    # throw error if response is not successful        
    else:
        print(f"Failed to fetch data for keyword '{keyword}'")

    return data

def prefill_database(data, keyword):
    '''add data to database
    --- data: json data from google maps api'''

    # # check if data is empty
    # if not data:
    #     print(f"No data found for keyword '{keyword}'")
    #     return
    
    # make sure data is not empty
    # loop through the data and add to database
    if data:
        for place in data.get("results", []):
            vendor = Vendor(
                name=place['name'],
                service_type=keyword,
                address=place.get('vicinity', 'N/A'),
                city=place.get('vicinity', 'N/A'),
                contact=place.get('vicinity', 'N/A'),
                hours=place.get('vicinity', 'N/A'),
                picture_url=place.get('vicinity', 'N/A')
            )
            db.session.add(vendor)
            db.session.commit()
            #print(f"Vendor '{vendor.name}' added to the
    return

# Fetch Google Maps API key from environment variables
GOOGLE_API_KEY = os.getenv("google_api_key")  # Updated to match your .env key
#LOCATION = "Sicily"
LOCATION = "37.6,13.4"  # Latitude and longitude for Sicily
RADIUS = 1000000  # 100 km radius
BASE_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

# list of keywords
keywords = ["wedding", "venue", "bridal", "event planner", "photographer", "bride", "wedding planer"]

if __name__ == "__main__":
    with app.app_context():
        # call google maps api for each keyword
        for keyword in keywords:
            params = {
                "key": GOOGLE_API_KEY,
                "location": LOCATION,
                "radius": RADIUS,
                "keyword": keyword
            }
            data = get_google_maps_data(params) # get data from google maps api
            prefill_database(data, keyword) # add data to database

            if data:
                for place in data.get("results", []):
                    print("-" * 40)
                    print(f"Name: {place['name']}")
                    print(f"Address: {place.get('vicinity', 'N/A')}")
                    print(f"Rating: {place.get('rating', 'N/A')}")
                    print(f"User Ratings Total: {place.get('user_ratings_total', 'N/A')}")
                    print(f"Types: {', '.join(place.get('types', []))}")
                    print(f"Business Status: {place.get('business_status', 'N/A')}")
                    print(f"Place ID: {place.get('place_id', 'N/A')}")
                    print(f"Location: {place['geometry']['location']['lat']}, {place['geometry']['location']['lng']}")
                    print("-" * 40)
        


