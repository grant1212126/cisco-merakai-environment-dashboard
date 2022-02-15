from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from DashboardApp.models import WeatherOptions, Location, Sensor, DataPoint

from lib import meraki, weather

import datetime
import json
from .forms import DateTimeForm
# Regression imports
import numpy as np
import re
from sklearn.linear_model import LinearRegression

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
    elif request.POST.get("edit"):  # Edit sensor object
        sensor = Sensor.objects.get(id=request.POST.get("id"))
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

@login_required
def index(request):
    locations, selected_location = \
        list_with_selected(Location.objects.all(), request.POST.get("select"))

    context = {
        "locations": locations,
        "selected_location": selected_location,
        "form": DateTimeForm(request.POST or None),

    }
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


    # Preliminary regression prediction testing
    # Ugly, I know, pester me about that later (no really, do pester me)
    time = [p[1].strftime("%m-%d-%Y %H:%M:%S") for p in humidity_data]
    time = np.array([re.split('-|:| ',a) for a in time]).astype(int)
    time = time[:,1:5]
    time = np.delete(time,1,1)
    humidity = np.array([p[0] for p in humidity_data]).astype(int)

    time_hum_model = LinearRegression()
    time_hum_model.fit(time, humidity)
    #theta0 = time_hum_model.intercept_
    #theta1, theta2, theta3 = time_hum_model.coef_
    to_predict = (datetime.datetime.now() + datetime.timedelta(minutes=30))

    hum_prediction = time_hum_model.predict([[int(to_predict.day), int(to_predict.hour), int(to_predict.minute)]]).round(2)
    print(hum_prediction)[0]


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
