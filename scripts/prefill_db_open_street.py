# TODO: explore alternative open source data sources for geocoding and place details

import requests

print('Hello World')

overpass_url = "https://overpass-api.de/api/interpreter"
query = """
[out:json][timeout:50];
area["ISO3166-2"="IT-82"][admin_level=4]; // Sicily

(
  node["shop"="photo"](area);
  node["craft"="photographer"](area);
  node["office"="event_planner"](area);
  node["shop"="wedding"](area);
  node["amenity"="restaurant"](area);
  node["amenity"="banquet_hall"](area);
  node["shop"="florist"](area);
  node["shop"="jewelry"](area);
  node["shop"="hairdresser"](area);
  node["shop"="beauty"](area);
) -> .weddingbiz;

out center tags;
"""

response = requests.post(overpass_url, data={"data": query})
data = response.json()

print(data)

for el in data["elements"]:
    tags = el.get("tags", {})
    name = tags.get("name", "No name")
    addr = ", ".join(
        filter(None, [
            tags.get("addr:street"),
            tags.get("addr:housenumber"),
            tags.get("addr:city"),
        ])
    )
    phone = tags.get("phone", tags.get("contact:phone", ""))
    website = tags.get("website", tags.get("contact:website", ""))
    lat, lon = el["lat"], el["lon"]
    
    print(f"{name} | {addr} | {phone} | {website} | {lat}, {lon}")
