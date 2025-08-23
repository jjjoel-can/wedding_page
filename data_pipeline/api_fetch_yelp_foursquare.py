
import requests
import json
from yelpapi import YelpAPI
import config
from dotenv import load_dotenv
import logging
import os
import sys

# Configure logging
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Logs only to a file named 'app.log' in the same directory
logging.basicConfig(
    filename='outputs/api_fetch_yelp_foursquare.log',
    filemode='a',  # 'a' for append, 'w' for overwrite
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
load_dotenv()

# --- API Key Validation ---
YELP_API_KEY = os.getenv("yelp_api_key")
FSQ_API_KEY = os.getenv("four_square_api_key")

if not YELP_API_KEY:
    logging.error("Yelp API key not found. Make sure it's set in your .env file.")
    sys.exit("Exiting: Missing Yelp API Key.")
if not FSQ_API_KEY:
    logging.error("Foursquare API key not found. Make sure it's set in your .env file as 'four_square_api_key'.")
    sys.exit("Exiting: Missing Foursquare API Key.")

# Initialize Yelp API client
yelp_api = YelpAPI(YELP_API_KEY)

# Dynamically construct the path relative to the current script's directory
output_path = os.path.join(os.path.dirname(__file__), "outputs", "yelp_fsq_vendors.json")
# Ensure the output directory exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

def test_foursquare_auth():
    """Test if Foursquare API key is working"""
    #url = "https://api.foursquare.com/v3/places/search"
    url = "https://places-api.foursquare.com/places/search"
    # headers = {
    #     "Authorization": f"Bearer {FSQ_API_KEY}",
    #     "accept": "application/json"
    # }

    headers = {
        "accept": "application/json",
        "X-Places-Api-Version": "2025-06-17",
        "authorization": f"Bearer {FSQ_API_KEY}" # Added "Bearer " prefix
    }
    params = {"query": "restaurant", "near": "New York, NY", "limit": 1}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Foursquare API is working! Found {len(data.get('results', []))} results")
        return True
    except Exception as e:
        print(f"❌ Foursquare API test failed: {e}")
        return False


def fetch_yelp_data():
    ''' Fetches wedding vendors from Yelp for specified cities and categories.'''
    vendors = []
    logging.info("Starting Yelp data fetch...")
    for city in config.SICILY_CITIES:
        for category in config.WEDDING_CATEGORIES:
            try:
                # The Yelp Fusion API is used for business searches. [docs.developer.yelp.com](https://docs.developer.yelp.com/docs/fusion-intro)
                response = yelp_api.search_query(categories=category, location=f"{city}, Italy", limit=50)
                businesses = response.get("businesses", [])
                for biz in businesses:
                    vendors.append({
                        "name": biz.get("name"),
                        "service_type": category,
                        "address": " ".join(biz.get("location", {}).get("display_address", [])),
                        "city": biz.get("location", {}).get("city"),
                        "contact": biz.get("phone"),
                        "picture_url": biz.get("image_url"),
                        "website": biz.get("url"),
                        "source": "Yelp"
                    })
                logging.info(f"Fetched {len(businesses)} Yelp results for '{category}' in {city}")
            except Exception as e:
                logging.error(f"Yelp API error for {city}/{category}: {e}")
    return vendors

def fetch_foursquare_data():
    ''' Fetches wedding vendors from Foursquare for specified cities and categories. '''
    vendors = []
    #url = "https://api.foursquare.com/v3/places/search"
    url = "https://places-api.foursquare.com/places/search"
    
    # FIXED: Proper Bearer token format for Foursquare API v3
    headers = {
        "accept": "application/json",
        "X-Places-Api-Version": "2025-06-17",
        "authorization": f"Bearer {FSQ_API_KEY}" # Added "Bearer " prefix
    }
    
    logging.info("Starting Foursquare data fetch...")
    for city in config.SICILY_CITIES:
        for category in config.WEDDING_CATEGORIES:
            # Foursquare uses a generic 'query' and a 'near' parameter for location
            params = {"query": category, "near": f"{city}, IT", "limit": 50, "sort": "RELEVANCE"}
            try:
                response = requests.get(url, params=params, headers=headers)
                # This will raise an HTTPError for bad responses (4xx or 5xx)
                response.raise_for_status() 
                
                data = response.json()
                places = data.get("results", [])
                
                for place in places:
                    # Gracefully handle missing data using .get()
                    location = place.get("location", {})
                    vendors.append({
                        "name": place.get("name"),
                        "service_type": category,
                        "address": location.get("formatted_address"),
                        "city": location.get("locality"),
                        "contact": None,  # Foursquare V3 Search doesn't typically return phone numbers
                        "picture_url": None, # Foursquare V3 Search doesnt return picture urls. You need a separate call
                        "website": None, # Foursquare V3 Search doesnt return a website. You need a separate call
                        "source": "Foursquare"
                    })
                logging.info(f"Fetched {len(places)} Foursquare results for '{category}' in {city}")
            
            # Catch specific request exceptions for better error logging
            except requests.exceptions.HTTPError as http_err:
                logging.error(f"Foursquare HTTP error for {city}/{category}: {http_err} - Response: {response.text}")
            except requests.exceptions.RequestException as req_err:
                logging.error(f"Foursquare Request error for {city}/{category}: {req_err}")
            except Exception as e:
                logging.error(f"An unexpected Foursquare API error occurred for {city}/{category}: {e}")
    return vendors

def main():
    test_foursquare_auth()  # Test Foursquare API key before proceeding
    #yelp_vendors = fetch_yelp_data()
    #foursquare_vendors = fetch_foursquare_data()
    
    all_vendors = fetch_yelp_data() + fetch_foursquare_data()
    #all_vendors = foursquare_vendors

    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(all_vendors, f, indent=4, ensure_ascii=False)
        
    logging.info(f"Process complete. Fetched {len(all_vendors)} total vendors.")
    print(f"Data saved to {output_path}")


if __name__ == "__main__":
    main()