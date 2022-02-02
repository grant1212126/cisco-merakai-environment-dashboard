#
# Meraki Dashboard API wrappers
#

import os
import requests

class MerakiError(BaseException):
    def __init__(self, status, message):
        super().__init__(f"{status}: {message}")

# Base URL for the Meraki API
base_url = "https://api.meraki.com/api/v1"

# Our API key is always in this environment variable
apikey = os.getenv("MERAKI_DASHBOARD_API_KEY")

def read_sensor(org_id, serial, metric):
    # API endpoint
    url = f"{base_url}/organizations/{org_id}/sensor/readings/latest"
    # GET parameters
    url += f"?serials[]={serial}&metrics[]={metric}"
    # Perform request
    resp = requests.get(url, headers={"X-Cisco-Meraki-API-Key": apikey})
    if resp.status_code != 200:
        raise MerakiError(resp.status_code, resp.content)
    # Parse response
    return resp.json()[0]["readings"][0][metric]

def read_occp(org_id, serial):
    url = f"{base_url}/devices/{serial}/camera/analytics/live"
    resp = requests.get(url, headers={"X-Cisco-Meraki-API-Key": apikey})
    if resp.status_code != 200:
        raise MerakiError(resp.status_code, resp.content)
    # NOTE: later on we might want to add more flexibility, but for
    # now the occupancy of the first zone seems to be a reasonable
    # thing to store
    return resp.json()["zones"]["0"]["person"]

def get_devices(org_id):
    url = f"{base_url}/organizations/{org_id}/devices"
    resp = requests.get(url, headers={"X-Cisco-Meraki-API-Key": apikey})
    if resp.status_code != 200:
        raise MerakiError(resp.status_code, resp.content)
    return resp.json()
