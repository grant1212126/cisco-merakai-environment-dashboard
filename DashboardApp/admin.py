from django.contrib import admin
from DashboardApp.models import Location, Sensor, DataPoint

# Registers the models to be edited on the admin site

admin.site.register(Location)
admin.site.register(Sensor)
admin.site.register(DataPoint)