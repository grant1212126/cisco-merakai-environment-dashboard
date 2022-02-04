from django.db import models
from django.utils.translation import gettext_lazy as _

class MerakiSensor(models.TextChoices):
	"""Monitorable Meraki sensors
	"""
	TEMPERATURE = "TM", _("Temperature")
	HUMIDITY    = "HD", _("Humidity")
	OCCUPANCY   = "OC", _("Occupancy")

class MerakiDataSource(models.Model):
	"""Represents a sensor on a Meraki device that we monitor, for now its either:
		1. MT10 temperature sensor
		2. MT10 humidity sensor
		3. MV12WE occupancy data
	"""

	# Unique identifier of this data source
	id = models.AutoField(unique=True, primary_key=True)

	# Organization ID the device belongs to
	org_id = models.CharField(max_length=64)

	# Serial number of device monitored by the data source
	serial = models.CharField(max_length=64)

	# Sensor on device monitored by the data source
	sensor = models.CharField(max_length=2, choices=MerakiSensor.choices)

	# Polling interval (in seconds)
	interval = models.IntegerField()

	# User friendly description
	description = models.TextField(blank=True)

	def __str__(self):
		return f"{self.id}({self.serial}: {self.description})"

class DataPoint(models.Model):
	"""Represents a data point collected by the data gathering daemon
	"""

	# Source the data was collected from
	ds_id = models.ForeignKey(MerakiDataSource, on_delete=models.CASCADE)

	# Type of sensor the data orginated from
	sensor = models.CharField(max_length=2, choices=MerakiSensor.choices)

	# Timestamp the data was collected at
	tstamp = models.DateTimeField(auto_now_add=True)

	# Value of the data point
	# NOTE: we might need non-float data later on
	value = models.FloatField()
