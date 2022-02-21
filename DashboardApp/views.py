from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from DashboardApp.models import WeatherOptions, Location, Sensor, DataPoint

from datetime import datetime
from scipy.interpolate import interp1d
import numpy as np

from lib import meraki, weather


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

class Graph:
    def __init__(self, label, func, begin, end):
        self.label = label
        self.func = func
        self.begin = begin
        self.end = end

def get_graphs(sensors, kind, interp_kind):
    graphs = []
    min_x = np.inf
    max_x = -np.inf

    for sensor in sensors:
        # Filter humidity data for the current sensor
        humidity = DataPoint.objects.filter(kind=kind, sensor=sensor)

        # Skip sensor if no data was collected
        if not humidity:
            continue

        # Interpolate function from data
        x = []
        y = []
        for p in humidity:
            x.append(p.tstamp.timestamp())
            y.append(p.value)

        func = interp1d(x, y, kind=interp_kind, bounds_error=False)
        begin = x[0]
        end = x[-1]

        # Add sensor info
        graphs.append(Graph(sensor.description, func, begin, end))

        # Find largest interval
        if begin < min_x:
            min_x = begin
        if end > max_x:
            max_x = end

    if len(graphs) > 0:
        return np.linspace(min_x, max_x, 200), graphs
    else:
        return None, None

@login_required
def filter_latest(request):
    location = Location.objects.get(id=request.GET.get("location"))
    sensors = Sensor.objects.filter(location=location)

    hd_x, hd_graphs = get_graphs(sensors, DataPoint.Kind.HD, "linear")
    tm_x, tm_graphs = get_graphs(sensors, DataPoint.Kind.TM, "linear")
    oc_x, oc_graphs = get_graphs(sensors, DataPoint.Kind.OC, "nearest")

    def cleanup_samples(x, graph):
        samples = []
        for y in graph.func(x):
            samples.append(None if np.isnan(y) else y)
        return samples

    data = {}

    if hd_x is not None:
        data["humidity_data"] = {
            "labels": [ datetime.fromtimestamp(x).strftime("%m-%d-%Y %H:%M:%S") for x in hd_x ],
            "datasets":[ {
                    "label": f"{graph.label} humidity %",
                    "data": cleanup_samples(hd_x, graph),
                    "backgroundColor": "#00ffff",
                    "borderColor": "#00ffff",
                    "pointRadius": 2.5,
                } for graph in hd_graphs
            ]
        }

    if tm_x is not None:
        data["temperature_data"] = {
            "labels": [ datetime.fromtimestamp(x).strftime("%m-%d-%Y %H:%M:%S") for x in tm_x ],
            "datasets":[ {
                    "label": f"{graph.label} temperature C",
                    "data": cleanup_samples(tm_x, graph),
                    "backgroundColor": "#ff7f00",
                    "borderColor": "#ff7f00",
                    "pointRadius": 2.5,
                } for graph in tm_graphs
            ]
        }

    if oc_x is not None:
        data["occupancy_data"] = {
            "labels": [ datetime.fromtimestamp(x).strftime("%m-%d-%Y %H:%M:%S") for x in oc_x ],
            "datasets":[ {
                    "label": f"{graph.label} occupancy",
                    "data": cleanup_samples(oc_x, graph),
                    "backgroundColor": "#7cfc00",
                    "borderColor": "#7cfc00",
                    "pointRadius": 2.5,
                } for graph in oc_graphs
            ]
        }

    # Get latest readings if present
    def val_or_none(p):
        if p is None:
            return None
        else:
            return p.value

    data["latest_hum"] = val_or_none(DataPoint.objects.filter(kind=DataPoint.Kind.HD).last())
    data["latest_temp"] = val_or_none(DataPoint.objects.filter(kind=DataPoint.Kind.TM).last())
    data["latest_occ"] = val_or_none(DataPoint.objects.filter(kind=DataPoint.Kind.OC).last())

    wopt = WeatherOptions.objects.first()
    if wopt:
        data["latest_weather"] = weather.read_loc_weather(wopt.lat, wopt.lon)

    return JsonResponse(data=data, safe=False)
