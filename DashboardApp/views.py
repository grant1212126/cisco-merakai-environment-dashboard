from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import DataPoint
from DashboardApp.models import DataPoint
import meraki
import datetime



# Cisco API handle
dashboard = meraki.DashboardAPI("6bec40cf957de430a6f1f2baa056b99a4fac9ea0",suppress_logging=True)

# List of organizations
def index(request):
    return render(request, "index.html", {
        "orgs": dashboard.organizations.getOrganizations()
    })

# Networks per org
def networks(request, org_id):
    return render(request, "networks.html", {
        "org": dashboard.organizations.getOrganization(org_id),
        "nets": dashboard.organizations.getOrganizationNetworks(org_id),
        })

# Devices per org
def devices(request, org_id):
    return render(request, "devices.html", {
        "org": dashboard.organizations.getOrganization(org_id),
        "devs": dashboard.organizations.getOrganizationDevices(org_id),
        })


# Feeds data to charts.html
def visualize_data(request):
    data = {
        "humidity_data": DataPoint.objects.filter(
            sensor = "HD").values_list("value","tstamp"),
        "temperature_data": DataPoint.objects.filter(
            sensor = "TM").values_list("value","tstamp"),
        "occupancy_data": DataPoint.objects.filter(
            sensor = "OC").values_list("value","tstamp"),
    }

    # Dictionaries structured in a Chart JS compatible way
    if request.is_ajax():

        humidity_data = {
            "labels": [data[1].strftime("%m-%d-%Y %H:%M:%S") for data in data["humidity_data"]],
            "datasets":[{
                "label": "Humidity",
                "data": [data[0] for data in data["humidity_data"]],
                "backgroundColor": "#00ffff",
                "borderColor": "#00ffff",
                "pointRadius": 2.5,
            }]
        }

        temperature_data = {
            "labels": [data[1].strftime("%m-%d-%Y %H:%M:%S") for data in data["temperature_data"]],
            "datasets":[{
                "label": "Temperature",
                "data": [data[0] for data in data["temperature_data"]],
                "backgroundColor": "#FF7F00",
                "borderColor": "#FF7F00",
                "pointRadius": 2.5,

            }]
        }

        occupancy_data = {
            "labels": [data[1].strftime("%m-%d-%Y %H:%M:%S") for data in data["occupancy_data"]],
            "datasets":[{
                "label": "Occupancy",
                "data": [data[0] for data in data["occupancy_data"]],
                "backgroundColor": "#7CFC00",
                "borderColor": "#7CFC00",
                "pointRadius": 2.5,

            }]
        }

        # Json response data
        chart_data  = {
            "humidity_data": humidity_data,
            "temperature_data": temperature_data,
            "occupancy_data": occupancy_data,
            "latest_hum": [data[0] for data in data["humidity_data"]][-1],
            "latest_temp": [data[0] for data in data["temperature_data"]][-1],
            "latest_occ":[data[0] for data in data["occupancy_data"]][-1]
        }

        
        return JsonResponse(data = chart_data , safe = False)

    return render(request, "charts.html")


def data(request, org_id):
    
    return render(request, "data.html", {
        "org": dashboard.organizations.getOrganization(org_id),
        "devs": dashboard.organizations.getOrganizationDevices(org_id),
        "data": DataPoint.objects.all(),
    })

