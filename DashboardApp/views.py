from django.shortcuts import render
from django.http import HttpResponse
import meraki

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
