#
# OpenWeatherMap API wrappers
#

import gzip
import json
import os
import pickle
import requests


# Absolute path to city list file
city_list = os.path.join(os.path.dirname(__file__), "city.list.pickled")

# Base URL for the OpenWeatherMap API
base_url = "https://api.openweathermap.org/data/2.5"

# Our API key is always in this environment variable
apikey = os.getenv("OPENWEATHERMAP_API_KEY")

class OpenWeatherMapError(BaseException):
    def __init__(self, status, message):
        super().__init__(f"{status}: {message}")

def read_city_weather(city):
    # API endpoint
    url = f"{base_url}/weather"
    # GET parameters
    url += f"?q={city}&app_id={apikey}"
    # Perform request
    resp = requests.get(url)
    if resp.status_code != 200:
        raise OpenWeatherMapError(resp.status_code, resp.content)
    # Parse response
    return resp.json()

def read_loc_weather(lat, lon):
    # API endpoint
    url = f"{base_url}/weather"
    # GET parameters
    url += f"?lat={lat}&lon={lon}&app_id={apikey}"
    # Perform request
    resp = requests.get(url)
    if resp.status_code != 200:
        raise OpenWeatherMapError(resp.status_code, resp.content)
    # Parse response
    return resp.json()

def search_city(name):
    with open(city_list, "rb") as file:
        lookup = pickle.load(file)
    return lookup.get(name)
