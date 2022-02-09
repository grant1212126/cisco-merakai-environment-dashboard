from django.db import models

class WeatherOptions(models.Model):
    """Weather API parameter configuration, for now this is global
    """

    # Geographical coordinates for the location
    lat = models.FloatField()
    lon = models.FloatField()

    # User friendly description of the location
    description = models.TextField(blank=True)

class Location(models.Model):
    """Represents a grouping of sensors
    """

    # Name of the location
    name = models.CharField(max_length=64, unique=True)
    # User friendly description
    description = models.TextField(blank=True)

class Sensor(models.Model):
    """Represents a Meraki sensor
    """

    class Kind(models.TextChoices):
        """Kind of sensors
        """
        CAM = "Camera"          # E.g. MV12WE camera
        ENV = "Environmental"   # E.g. MT10 environmental sensor

    # Org ID and Serial required for accessing the device
    # These *must* be unique together, this prevents duplicate sensors
    org_id = models.CharField(max_length=64)
    serial = models.CharField(max_length=64)

    # Kind of sensor (this must always match the device type reported by
    # the Cisco API, we save it to make it easier to determine what API
    # to call for gathering data)
    kind = models.CharField(max_length=13, choices=Kind.choices)

    # Location the device is installed at
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    # User friendly description
    description = models.TextField(blank=True)

    # Polling interval (in seconds)
    interval = models.IntegerField()

    class Meta:
        unique_together = (("org_id", "serial"),)

class DataPoint(models.Model):
    """Represents a data point collected by the data gathering daemon
    """

    class Kind(models.TextChoices):
        """Kinds of data points
        """
        TM  = "Temperature"
        HD  = "Humidity"
        OC  = "Occupancy"

    # Location the data was collected from
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    # Sensor the data was collected from
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)

    # Kind of data point
    kind = models.CharField(max_length=11, choices=Kind.choices)

    # Timestamp the data was collected at
    tstamp = models.DateTimeField(auto_now_add=True)

    # Value of the data point
    value = models.FloatField()
