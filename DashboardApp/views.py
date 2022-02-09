from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from DashboardApp.models import WeatherOptions, Location, Sensor, DataPoint

from lib import meraki, weather

import datetime
import json

def list_with_selected(query, selected_id):
    result = []
    selected = None
    for obj in query:
        cur_dict = model_to_dict(obj)
        if str(obj.id) == selected_id:
            selected = cur_dict
        result.append(cur_dict)
    if selected is None and len(result) > 0:
        selected = result[0]
    return result, selected

@login_required
def settings_weather(request):
    context = {}

    opts = WeatherOptions.objects.first()
    from_search = False
    if request.POST.get("search"):
        city_name = request.POST.get("city")
        city = weather.search_city(city_name)
        if city:
            country = city["country"]
            state = city["state"]
            if state != "":
                context["description"] = f"{city_name}, {state}, {country}"
            else:
                context["description"] = f"{city_name}, {country}"
            context["lat"] =  city["coord"]["lat"]
            context["lon"] =  city["coord"]["lon"]
        from_search = True
    elif request.POST.get("edit"):
        if opts is None:
            opts = WeatherOptions()
        opts.description = request.POST.get("description")
        opts.lat = float(request.POST.get("lat"))
        opts.lon = float(request.POST.get("lon"))
        opts.save()

    if not from_search and opts:
        context["description"] = opts.description
        context["lat"] = opts.lat
        context["lon"] = opts.lon

    return render(request, "settings/weather.html", context=context)

@login_required
def settings_locations(request):
    context = {}

    # Perform any requested actions
    if request.POST.get("add"):
        location = Location(
            name=request.POST.get("name"),
            description=request.POST.get("description"))
        location.save()
    elif request.POST.get("edit"):
        location = Location.objects.get(id=request.POST.get("id"))
        location.name = request.POST.get("name")
        location.description = request.POST.get("description")
        location.save()
    elif request.POST.get("delete"):
        location = Location.objects.get(id=request.POST.get("id"))
        location.delete()

    locations, selected_location = \
        list_with_selected(Location.objects.all(), request.POST.get("select"))

    context["locations"] = locations
    context["selected_location"] = selected_location

    # Render page
    return render(request, "settings/locations.html", context=context)

@login_required
def settings_sensors(request):
    context = {}

    # Obtain Meraki devices from Dashboard API
    # TODO: Maybe cache this somewhere
    meraki_devices = []
    meraki_dev_idx = 0
    for org in meraki.get_orgs():
        for dev in meraki.get_devices(org["id"]):
            if dev["productType"] == "camera":
                kind = Sensor.Kind.CAM
            elif dev["productType"] == "sensor":
                kind = Sensor.Kind.ENV
            else:
                continue

            meraki_devices.append({
                "idx": meraki_dev_idx,
                "org_id": org["id"],
                "serial": dev["serial"],
                "name": dev["name"] if dev["name"] else "",
                "kind": kind
            })
            meraki_dev_idx += 1

    # Perform any requested actions
    if request.POST.get("add"):     # Add sensor object for Meraki device
        meraki_dev_idx = int(request.POST.get("meraki_dev_idx"))
        dev = meraki_devices[meraki_dev_idx]
        sensor = Sensor(
            org_id=dev["org_id"],
            serial=dev["serial"],
            kind=dev["kind"],
            description=dev["name"],
            interval=60)
        sensor.save()
    elif request.POST.get("edit"):  # Edit sensor object
        sensor = Sensor.objects.get(id=request.POST.get("id"))
        if request.POST.get("location") != "null":
            sensor.location = Location.objects.get(id=request.POST.get("location"))
        sensor.description = request.POST.get("description")
        sensor.interval = int(request.POST.get("interval"))
        sensor.save()
    elif request.POST.get("delete"):  # Delete sensor object
        sensor = Sensor.objects.get(id=request.POST.get("id"))
        sensor.delete()

    # Get selected sensor
    sensors, selected_sensor = \
        list_with_selected(Sensor.objects.all(), request.POST.get("select"))

    context["meraki_devices"] = meraki_devices
    context["locations"] = [ model_to_dict(loc) for loc in Location.objects.all() ]
    context["sensors"] = sensors
    context["selected_sensor"] = selected_sensor


    return render(request, "settings/sensors.html", context=context)

# Feeds data to index.html
@login_required
def visualize_data(request):
    data = {
        "humidity_data": DataPoint.objects.filter(
            kind = DataPoint.Kind.HD).values_list("value", "tstamp"),
        "temperature_data": DataPoint.objects.filter(
            kind = DataPoint.Kind.TM).values_list("value", "tstamp"),
        "occupancy_data": DataPoint.objects.filter(
            kind = DataPoint.Kind.OC).values_list("value", "tstamp"),
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

        
        return JsonResponse(data=chart_data, safe=False)

    return render(request, "index.html")
