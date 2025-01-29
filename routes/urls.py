from django.urls import path
from .views import get_route

urlpatterns = [
    path("route/", get_route, name="get_route"),
]
