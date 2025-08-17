import requests
import json
from yelpapi import YelpAPI
import config
from dotenv import load_dotenv
import logging  # Added for better debugging
import os

# Dynamically construct the path relative to the current directory
output_path = os.path.join(os.path.dirname(__file__), "outputs", "yelp_fsq_vendors.json")

load_dotenv()
logging.basicConfig(level=logging.INFO)  # Set up logging

yelp_api = YelpAPI(os.getenv("yelp_api_key"))
fsq_api_key = os.getenv("four_square_api_key")

def fetch_yelp_data():
    vendors = []
    for city in config.SICILY_CITIES:  # Corrected from typo
        for category in config.WEDDING_CATEGORIES:
            try:
                response = yelp_api.search_query(categories=category, location=f"{city}, Italy", limit=50)
                for biz in response.get("businesses", []):
                    vendors.append({
                        "name": biz["name"],
                        "service_type": category,
                        "address": " ".join(biz.get("location", {}).get("display_address", [])),
                        "city": biz["location"].get("city"),
                        "contact": biz.get("phone"),
                        "hours": json.dumps(biz.get("hours")),  # Stringify for storage
                        "picture_url": biz["image_url"],
                        "website": biz.get("url")
                    })
                logging.info(f"Fetched {len(response.get('businesses', []))} Yelp results for {category} in {city}")
            except Exception as e:
                logging.error(f"Yelp API error for {city}/{category}: {e}")
    return vendors

def fetch_foursquare_data():
    vendors = []
    url = "https://api.foursquare.com/v3/places/search"
    headers = {"Authorization": fsq_api_key}
    for city in config.SICILY_CITIES:  # Corrected from typo (was "SIC nyel_CITIES")
        for category in config.WEDDING_CATEGORIES:
            params = {"query": category, "near": f"{city}, IT", "limit": 50}
            try:
                response = requests.get(url, params=params, headers=headers).json()
                for place in response.get("results", []):
                    vendors.append({
                        "name": place["name"],
                        "service_type": category,
                        "address": place.get("location", {}).get("formatted_address"),
                        "city": place["location"].get("locality"),
                        "contact": place.get("tel"),
                        "website": place.get("website")
                    })
                logging.info(f"Fetched {len(response.get('results', []))} Foursquare results for {category} in {city}")
            except Exception as e:
                logging.error(f"Foursquare API error for {city}/{category}: {e}")
    return vendors

def main():
    all_vendors = fetch_yelp_data() + fetch_foursquare_data()
    #with open("outputs/yelp_fsq_vendors.json", "w") as f:  # Assumes outputs/ subfolder
    with open(output_path, "w") as f:  # Assumes outputs/ subfolder
        json.dump(all_vendors, f)
    print(f"Fetched {len(all_vendors)} vendors from Yelp/Foursquare.")

if __name__ == "__main__":
    main()