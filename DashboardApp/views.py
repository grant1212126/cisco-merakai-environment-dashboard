from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from DashboardApp.models import DataPoint, MerakiSensor, MerakiDataSource
from lib import meraki
import datetime
import json
from .forms import DateTimeForm

# Sets up add_device.html and adds device when posted
def add_device(request):
    class Device:
        def __init__(self, org_id, serial, description, supported_sensors):
            self.org_id = org_id
            self.serial = serial
            self.description = description
            self.supported_sensors = supported_sensors

    if request.method == "POST":
        org_id = request.POST.get("org_id")
        serial = request.POST.get("serial")
        description = request.POST.get("description")

        def add_sensor(sensor):
            ds = MerakiDataSource(org_id=org_id,
                    serial=serial,
                    description=description,
                    interval=interval,
                    sensor=sensor)
            ds.save()

        interval = 10 # FIXME: stop hard-coding this
        if request.POST.get("sensor_oc") == "on":
            add_sensor(MerakiSensor.OCCUPANCY)
        if request.POST.get("sensor_tm") == "on":
            add_sensor(MerakiSensor.TEMPERATURE)
        if request.POST.get("sensor_hd") == "on":
            add_sensor(MerakiSensor.HUMIDITY)

    elif request.is_ajax():
        org_id = request.GET.get("org_id")
        if not isinstance(org_id, str):
            raise ValueError()

        devices = []
        for meraki_dev in meraki.get_devices(org_id):
            print(meraki_dev)
            supported_sensors = []

            if meraki_dev["productType"] == "camera":
                supported_sensors.append(MerakiSensor.OCCUPANCY)
            elif meraki_dev["productType"] == "sensor":
                # TODO: we might want to check if a "sensor" device truly
                # supports these metrics, for now I am just assuming its
                # always gonna be an MT10
                supported_sensors.append(MerakiSensor.HUMIDITY)
                supported_sensors.append(MerakiSensor.TEMPERATURE)

            device = Device(org_id, meraki_dev["serial"],
                            meraki_dev["name"], supported_sensors)
            devices.append(device.__dict__)

        return JsonResponse(data=devices, safe=False)

    return render(request, "add_device.html")

# Feeds data to index.html
def visualize_data(request):




    data = {
        "humidity_data": DataPoint.objects.filter(
            sensor = "HD").values_list("value", "tstamp"),
        "temperature_data": DataPoint.objects.filter(
            sensor = "TM").values_list("value", "tstamp"),
        "occupancy_data": DataPoint.objects.filter(
            sensor = "OC").values_list("value", "tstamp"),
    }

    context = {
        'form': DateTimeForm(request.POST or None),
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

    return render(request, "index.html", context)



