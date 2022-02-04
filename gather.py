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
from DashboardApp.models import MerakiSensor, MerakiDataSource, DataPoint

# Job dispatcher function for each sensor type
def disp_temperature(ds):
	# print(f"Polling temperature from {ds}")

	# Poll temperature
	rh = meraki.read_sensor(ds.org_id, ds.serial, "temperature")["celsius"]

	# Add DataPoint
	dp = DataPoint(ds_id=ds,
				sensor=MerakiSensor.TEMPERATURE,
				value=20.0 + random.uniform(-2.0, 2.0))
	dp.save()

def disp_humidity(ds):
	# print(f"Polling humidity from {ds}")

	# Poll humidity
	rh = meraki.read_sensor(ds.org_id, ds.serial, "humidity")["relativePercentage"]

	# Add DataPoint
	dp = DataPoint(ds_id=ds,
				sensor=MerakiSensor.HUMIDITY,
				value=rh)
	dp.save()

def disp_occupancy(ds):
	# print(f"Polling occupancy from {ds}")

	# Poll occupancy from device
	occup = meraki.read_occp(ds.org_id, ds.serial)

	# Add DataPoint to database
	dp = DataPoint(ds_id=ds,
				sensor=MerakiSensor.OCCUPANCY,
				value=occup)
	dp.save()

dispatchers = {
	MerakiSensor.TEMPERATURE: disp_temperature,
	MerakiSensor.HUMIDITY: disp_humidity,
	MerakiSensor.OCCUPANCY: disp_occupancy,
}

def make_dispatcher(ds):
	"""Create data source specific dispatcher closure
		WARNING: do *not* try to inline this function into the loop below,
		Python's scoping rules will break everything
	"""
	return lambda: dispatchers[ds.sensor](ds)

for ds in MerakiDataSource.objects.all():
	# Schedule dispatcher to run at the correct interval
	schedule.every(ds.interval).seconds.do(make_dispatcher(ds))

# Run scheduled tasks forever
while True:
	schedule.run_pending()
	time.sleep(1)
