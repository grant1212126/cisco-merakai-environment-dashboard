from django.urls import path
from .views import index, networks, devices, data

urlpatterns = [
    path("", index, name="index"),
    path("<int:org_id>/networks", networks, name="networks"),
    path("<int:org_id>/devices", devices, name="devices"),
    path("<int:org_id>/data", data, name="data"),
]
