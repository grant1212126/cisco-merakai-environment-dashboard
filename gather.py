#!/usr/bin/env python
import copy
import django
import os
import random
import schedule
import time
from lib import meraki

# Load Django project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Dashboard.settings")
django.setup()

# Project specific imports
from DashboardApp.models import Sensor, DataPoint

def disp_camera(sensor):
    try:
        # Poll occupancy from device
        occup = meraki.read_occp(sensor.org_id, sensor.serial)

        # Add DataPoint to database
        dp = DataPoint(location=sensor.location,
                    sensor=sensor,
                    kind =DataPoint.Kind.OC,
                    value=occup)
        dp.save()
    except:
        pass

def disp_environmental(sensor):
    # Poll data
    data = meraki.read_sensor(sensor.org_id, sensor.serial)
    readings = data[0]["readings"]

    for metric in readings:
        if metric["metric"] == "humidity":
            dp = DataPoint(location=sensor.location,
                sensor=sensor, kind=DataPoint.Kind.HD,
                value=metric["humidity"]["relativePercentage"])
            dp.save()
        elif metric["metric"] == "temperature":
            dp = DataPoint(location=sensor.location,
                sensor=sensor, kind=DataPoint.Kind.TM,
                value=metric["temperature"]["celsius"])
            dp.save()


dispatchers = {
    Sensor.Kind.CAM: disp_camera,
    Sensor.Kind.ENV: disp_environmental,
}

def make_dispatcher(sensor):
    """Create sensor kind specific dispatcher closure
        WARNING: do *not* try to inline this function into the loop below,
        Python's scoping rules will break everything
    """
    return lambda: dispatchers[sensor.kind](sensor)

for sensor in Sensor.objects.all():
    # Schedule dispatcher to run at the correct interval
    schedule.every(sensor.interval).seconds.do(make_dispatcher(sensor))

# Run scheduled tasks forever
while True:
    schedule.run_pending()
    time.sleep(1)
