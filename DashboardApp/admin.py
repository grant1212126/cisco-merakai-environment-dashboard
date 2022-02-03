from django.contrib import admin
from DashboardApp.models import Location, Sensor, DataPoint

admin.site.register(Location)
admin.site.register(Sensor)
admin.site.register(DataPoint)
