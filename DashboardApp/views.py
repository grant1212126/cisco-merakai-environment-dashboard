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

def get_meraki_devices():
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
    return meraki_devices

@login_required
def settings_weather(request):
    context = {}

    opts = WeatherOptions.objects.first()
    if opts is None:
        opts = WeatherOptions()

    if request.POST.get("search"):
        city = request.POST.get("city")
        result = weather.search_city(city)
        if result:
            state = result["state"]
            country = result["country"]
            if state != "":
                description = f"{city}, {state}, {country}"
            else:
                description = f"{city}, {country}"

            opts.description = description
            opts.lat = float(result["coord"]["lat"])
            opts.lon = float(result["coord"]["lon"])
            opts.save()
    elif request.POST.get("edit"):
        opts.description = request.POST.get("description")
        opts.lat = float(request.POST.get("lat"))
        opts.lon = float(request.POST.get("lon"))
        opts.save()

    context["description"] = opts.description
    context["lat"] = opts.lat
    context["lon"] = opts.lon

    return render(request, "settings/weather.html", context=context)

@login_required
def settings_locations(request):
    context = {}
    selected_id = request.POST.get("select")

    # Perform any requested actions
    if request.POST.get("add"):
        location = Location(
            name=request.POST.get("name"),
            description=request.POST.get("description"))
        location.save()
        # Set selection to newly created location
        selected_id = str(location.id)
    elif request.POST.get("edit"):
        location = Location.objects.get(id=request.POST.get("id"))
        location.name = request.POST.get("name")
        location.description = request.POST.get("description")
        location.save()
        # Retain edited location as selected
        selected_id = str(location.id)
    elif request.POST.get("delete"):
        location = Location.objects.get(id=request.POST.get("id"))
        location.delete()

    locations, selected_location = \
        list_with_selected(Location.objects.all(), selected_id)

    context["locations"] = locations
    context["selected_location"] = selected_location

    # Render page
    return render(request, "settings/locations.html", context=context)

@login_required
def settings_sensors(request):
    context = {}
    selected_id = request.POST.get("select")

    # Obtain Meraki devices from Dashboard API
    meraki_devices = request.session.get("meraki_devices")
    if request.POST.get("refresh") or meraki_devices == None:
        meraki_devices = get_meraki_devices()
        request.session["meraki_devices"] = meraki_devices

    # Perform any requested actions
    if request.POST.get("add"):     # Add sensor object for Meraki device
        meraki_dev_idx = int(request.POST.get("meraki_dev_idx"))
        location_id = request.POST.get("location")
        dev = meraki_devices[meraki_dev_idx]
        sensor = Sensor(
            org_id=dev["org_id"],
            serial=dev["serial"],
            kind=dev["kind"],
            location=Location.objects.get(id=location_id),
            description=dev["name"],
            interval=60)
        sensor.save()
        # Set newly added sensor as selected
        selected_id = str(sensor.id)
    elif request.POST.get("edit"):  # Edit sensor object
        sensor = Sensor.objects.get(id=request.POST.get("id"))
        sensor.location = Location.objects.get(id=request.POST.get("location"))
        sensor.description = request.POST.get("description")
        sensor.interval = int(request.POST.get("interval"))
        sensor.save()
        # Retain edited sensor as selected
        selected_id = str(sensor.id)
    elif request.POST.get("delete"):  # Delete sensor object
        sensor = Sensor.objects.get(id=request.POST.get("id"))
        sensor.delete()

    # Get selected sensor
    sensors, selected_sensor = \
        list_with_selected(Sensor.objects.all(), selected_id)

    context["meraki_devices"] = meraki_devices
    context["locations"] = [ model_to_dict(loc) for loc in Location.objects.all() ]
    context["sensors"] = sensors
    context["selected_sensor"] = selected_sensor

    return render(request, "settings/sensors.html", context=context)

@login_required
def index(request):
    context = {}
    locations, selected_location = \
        list_with_selected(Location.objects.all(), request.POST.get("select"))
    context["locations"] = locations
    context["selected_location"] = selected_location
    return render(request, "index.html", context=context)

def chartify_data(timeseries, label, color):
    return {
        "labels": [p[1].strftime("%m-%d-%Y %H:%M:%S") for p in timeseries],
        "datasets":[{
            "label": label,
            "data": [p[0] for p in timeseries],
            "backgroundColor": color,
            "borderColor": color,
            "pointRadius": 2.5,
        }]
    }

@login_required
def filter_latest(request):
    location = Location.objects.get(id=request.GET.get("location"))

    humidity_data = DataPoint.objects.filter(kind=DataPoint.Kind.HD,
        location=location).values_list("value", "tstamp")
    temperature_data = DataPoint.objects.filter(kind=DataPoint.Kind.TM,
        location=location).values_list("value", "tstamp")
    occupancy_data = DataPoint.objects.filter(kind=DataPoint.Kind.OC,
        location=location).values_list("value", "tstamp")

    # Format data in a ChartJS compatible way
    chart_data = {
        "humidity_data": chartify_data(humidity_data, "Humidity", "#00ffff"),
        "temperature_data": chartify_data(temperature_data, "Temperature", "#ff7f00"),
        "occupancy_data": chartify_data(occupancy_data, "Occupancy", "#7cfc00"),
    }

    # Get latest readings if present
    if humidity_data:
        chart_data["latest_hum"] = humidity_data.last()[0]
    if temperature_data:
        chart_data["latest_temp"] = temperature_data.last()[0]
    if occupancy_data:
        chart_data["latest_occ"] = occupancy_data.last()[0]

    weather_opts = WeatherOptions.objects.first()
    if weather_opts:
        chart_data["latest_weather"] = \
            weather.read_loc_weather(weather_opts.lat, weather_opts.lon)

    return JsonResponse(data=chart_data, safe=False)
