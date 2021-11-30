from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import DataPoint
import meraki
import datetime



# Cisco API handle
dashboard = meraki.DashboardAPI(suppress_logging=True)

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


def visualize_data(request):
    data = {
        "humidity_data": DataPoint.objects.filter(
            sensor = "HD").values_list("value","tstamp"),
        "temperature_data": DataPoint.objects.filter(
            sensor = "TM").values_list("value","tstamp"),
        "occupancy_data": DataPoint.objects.filter(
            sensor = "OC").values_list("value","tstamp"),
    }

    if request.is_ajax():
        print("was AJAX")
        chart_data = {

                "humidity_data": [
                    [data[0] for data in data["humidity_data"]],
                    [data[1].strftime("%m-%d-%Y-%H:%M:%S") for data in data["humidity_data"]]
                ],
                "temperature_data": [
                    [data[0] for data in data["temperature_data"]],
                    [data[1].strftime("%m-%d-%Y-%H:%M:%S") for data in data["temperature_data"]]
                ],
                "occupancy_data": [
                    [data[0] for data in data["occupancy_data"]],
                    [data[1].strftime("%m-%d-%Y-%H:%M:%S") for data in data["occupancy_data"]]
                ],

        }

        return JsonResponse(data = chart_data, safe = False)

    return render(request, "charts.html")

