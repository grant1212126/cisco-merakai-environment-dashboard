from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.timezone import make_aware

from DashboardApp.models import WeatherOptions, Location, Sensor, DataPoint

# Imports from project library

from datetime import datetime
from scipy.interpolate import interp1d
import numpy as np

from lib import meraki, weather

# Helper function, takes in query set and idea and returns 2 things, object from query if matched and selected item

def list_with_selected(query, selected_id):

    result = []
    selected = None

    for obj in query: # for each object in the query input

        cur_dict = model_to_dict(obj) # standard django function, converts object to dictionary

        if str(obj.id) == selected_id: # if the object id (current item in the query) == the selected item is assigned
            selected = cur_dict
        result.append(cur_dict)

    if selected is None and len(result) > 0: # If no objects are matched and query is not empty, return first item in result
        selected = result[0] 


    return result, selected


# Return results from the API query, requests organisation and returns all devices for the organisation, effectively aggregates all items from all organisations into usable structure

def get_meraki_devices():

    meraki_devices = []
    meraki_dev_idx = 0

    for org in meraki.get_orgs(): # For each organisation

        for dev in meraki.get_devices(org["id"]): # For each organisation, get all devices associated

            # Checks device type, we only want to get informations from the cameras and sensors

            if dev["productType"] == "camera":
                kind = Sensor.Kind.CAM
            elif dev["productType"] == "sensor":
                kind = Sensor.Kind.ENV
            else:
                continue # Continue and ignore any device that is not a camera or sensor 

            # Append device information to the dictionary we want returned

            meraki_devices.append({
                "idx": meraki_dev_idx,
                "org_id": org["id"],
                "serial": dev["serial"],
                "name": dev["name"] if dev["name"] else "",
                "kind": kind
            })
            meraki_dev_idx += 1

    return meraki_devices # Return list of dictionaries of all the relevent device information 

# View to get and provide/ update information for the settings page for our weather functionality
#
# First recieves the users WeatherSettings object
#
# If the POST request contains "search", the function comapares the users desired city to use for weather against the applications database of available locations,
# the function then adds the match to the databse to display the weather information on the main dashboard
#
# If the POST request contains "edit", the function recieves the options the user has entered and directly edits the WeatherOptions instance to the inputed options.
#
# Finally, the function returns the HTML response to the application

@login_required
def settings_weather(request):
    context = {}

    # Recieves the first instance of the WeatherOptions model to be used, if none exists one is created for editing

    opts = WeatherOptions.objects.first()

    if opts is None:
        opts = WeatherOptions()

    if request.POST.get("search"):

        city = request.POST.get("city")
        result = weather.search_city(city)

        # If search doesent return any matches, no changes are made to the WeatherOptions instance

        if result: # If a match is made, saves options from said match into the Weather Options instance
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

        # Changes the WeatherOptions model to the users inputed options

        opts.description = request.POST.get("description")
        opts.lat = float(request.POST.get("lat"))
        opts.lon = float(request.POST.get("lon"))
        opts.save()

    context["description"] = opts.description
    context["lat"] = opts.lat
    context["lon"] = opts.lon

    return render(request, "settings/weather.html", context=context)

# View for the locations section of the settings page, 3 main options:
#
# If the POST request contains "add", the function takes in the information about the location they wish to add, and creates an instance of a locations model and saves it7
#
# If the POST request contains "edit", the function returns the instance of the location model they wish to edit, and updates said location with the entered information
#
# If the POST request contains "delete", the function searches for, and deletes the instance of loction that the user selected
#
# Finally, the updated list of locations is returned to the application to be displayed to the user 

@login_required
def settings_locations(request):
    context = {}
    selected_id = request.POST.get("select") # Recieves request

    # Perform any requested actions listed above in documentation
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

    # Updates and gets the list of locations that should be displayed on the page (with the updated changes from above)

    locations, selected_location = \
        list_with_selected(Location.objects.all(), selected_id)

    context["locations"] = locations
    context["selected_location"] = selected_location

    # Render page
    return render(request, "settings/locations.html", context=context)

# Used to display, change and add the Sensor model instances used in the application, if requested, performs one of four actions:
#
# If the user requests to refresh, the get_meraki_devices function is called to recieve the list of devices that the user has attatched to their organisation and returns 
#
# If the user requests to add a sensor, the ID of whatever sensor the user selects is recieved 
# and is then used alongside the location the user has selected to add said sensor to the
# location.
#
# If the user requests to edit a sensor, said sensor is pulled and the information the 
# user has entered is used to change said sensor with the desired information.
#
# If the user requests to delete a sensor, said sensor is pulled and then deleted in
# the database.
#
# Finally, the updated list of sensors is pulled and returned to be displayed in the
# application.

@login_required
def settings_sensors(request):
    context = {}
    selected_id = request.POST.get("select")

    # Obtain Meraki devices from Dashboard API
    meraki_devices = request.session.get("meraki_devices") # Gets all devices 

    if request.POST.get("refresh") or meraki_devices == None:
        meraki_devices = get_meraki_devices()
        request.session["meraki_devices"] = meraki_devices

    # Perform any requested actions
    if request.POST.get("add"):     # Add sensor object for Meraki device

        # Polls the meraki API to get the information

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

# View to show initial data on index page, pulls the locations and a location to be initially 
# selected and shown.

@login_required
def index(request):
    context = {}
    locations, selected_location = \
        list_with_selected(Location.objects.all(), request.POST.get("select"))
    context["locations"] = locations
    context["selected_location"] = selected_location
    return render(request, "index.html", context=context)

# Class for Graph display

class Graph:
    def __init__(self, label, func, begin, end):
        self.label = label
        self.func = func
        self.begin = begin
        self.end = end

# Helper function used to grab the latest data for all the sensors to then be put into the
# graphs. 

def get_graphs(sensors, begin_dt, end_dt, kind, interp_kind):
    graphs = []
    min_x = np.inf
    max_x = -np.inf

    for sensor in sensors:
        # Filter humidity data for the current sensor
        humidity = DataPoint.objects.filter(kind=kind, sensor=sensor,
            tstamp__range=(begin_dt, end_dt))

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

    # Return all the graphs created from the data, returns None if no graphs where created

    if len(graphs) > 0:
        return np.linspace(min_x, max_x, 100), graphs
    else:
        return None, None

# Function used to get the latest sensor data and create graphs from said data

@login_required
def filter_latest(request):

    # Gathers the date time range for the data and the location the user is viewing

    begin = make_aware(datetime.strptime(request.GET.get("begin"), "%Y-%m-%d %H:%M"))
    end = make_aware(datetime.strptime(request.GET.get("end"), "%Y-%m-%d %H:%M"))
    location = Location.objects.get(id=request.GET.get("location")) # Current location that the user is viewing
    sensors = Sensor.objects.filter(location=location)

    # gets the graphs for the three different data types we will be viewing

    hd_x, hd_graphs = get_graphs(sensors, begin, end, DataPoint.Kind.HD, "linear")
    tm_x, tm_graphs = get_graphs(sensors, begin, end, DataPoint.Kind.TM, "linear")
    oc_x, oc_graphs = get_graphs(sensors, begin, end, DataPoint.Kind.OC, "nearest")

    def cleanup_samples(x, graph):
        samples = []
        for y in graph.func(x):
            samples.append(None if np.isnan(y) else y)
        return samples

    data = {}

    # Creates graphs for the three different data types, if the data exists. 

    if hd_x is not None:
        data["humidity_data"] = {
            "labels": [ datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M") for x in hd_x ],
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
            "labels": [ datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M") for x in tm_x ],
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
            "labels": [ datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M") for x in oc_x ],
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

    # Latest data for the three data types

    data["latest_hum"] = val_or_none(DataPoint.objects.filter(kind=DataPoint.Kind.HD).last())
    data["latest_temp"] = val_or_none(DataPoint.objects.filter(kind=DataPoint.Kind.TM).last())
    data["latest_occ"] = val_or_none(DataPoint.objects.filter(kind=DataPoint.Kind.OC).last())

    # Latest weather data

    wopt = WeatherOptions.objects.first()
    if wopt:
        data["latest_weather"] = weather.read_loc_weather(wopt.lat, wopt.lon)

    return JsonResponse(data=data, safe=False) # Returns data as JSON 
