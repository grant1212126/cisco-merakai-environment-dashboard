from django.urls import path
from .views import add_device, visualize_data

urlpatterns = [
    path("", visualize_data, name="charts"),
    path("add_device/", add_device, name="add_device"),
]
