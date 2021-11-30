from django.shortcuts import render
from django.http import HttpResponse
from DashboardApp.models import DataPoint
import meraki

# Cisco API handle
dashboard = meraki.DashboardAPI("10a7351614bbbc50e3e2f91a53e15cb58636a6a6", suppress_logging=True)

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

def data(request, org_id):
    
    return render(request, "data.html", {
        "org": dashboard.organizations.getOrganization(org_id),
        "devs": dashboard.organizations.getOrganizationDevices(org_id),
        "data": DataPoint.objects.all(),
    })