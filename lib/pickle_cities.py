#
# Turn the city list into a pickled dictionary
#

import gzip
import json
import pickle
import requests

# URL to download gzipped city list from
city_list_url = "http://bulk.openweathermap.org/sample/city.list.json.gz"

# Unpack and parse blob
resp = requests.get(city_list_url)
data = json.loads(gzip.decompress(resp.content))

# Create lookup dictionary
lookup = {}
for entry in data:
    city = entry["name"]
    state = entry["state"]
    country = entry["country"]
    ent = {
        "country": entry["country"],
        "state": entry["state"],
        "coord": entry["coord"],
    }
    # Add multiple lookup entries
    lookup[city] = ent
    if state != "":
        lookup[f"{city}, {state}"] = ent
        lookup[f"{city}, {state}, {country}"] = ent
    lookup[f"{city}, {country}"] = ent

# Write result
with open("city.list.pickled", "wb") as file:
    pickle.dump(lookup, file)
