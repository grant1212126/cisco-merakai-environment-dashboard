from django.urls import path
from django.contrib.auth import views as auth_views

from DashboardApp.views import index, settings_weather, settings_locations, \
    settings_sensors, filter_latest

urlpatterns = [
    path("", index, name="index"),

    # Authentication
    path('auth/login/',
        auth_views.LoginView.as_view(template_name="auth/login.html",
            redirect_authenticated_user=True),
        name="auth/login"),
    path("auth/logout/", auth_views.LogoutView.as_view(), name="auth/logout"),

    # Configuration
    path("settings/weather/", settings_weather, name="settings/weather"),
    path("settings/locations/", settings_locations, name="settings/locations"),
    path("settings/sensors/", settings_sensors, name="settings/sensors"),

    # AJAX data providers
    path("filter/latest/", filter_latest, name="filter/latest")
]
