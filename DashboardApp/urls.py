from django.urls import path
from DashboardApp.views import visualize_data, \
    settings_weather, settings_locations, settings_sensors

urlpatterns = [
    path("", visualize_data, name="charts"),

    path("settings/weather/", settings_weather),
    path("settings/locations/", settings_locations),
    path("settings/sensors/", settings_sensors),
]
