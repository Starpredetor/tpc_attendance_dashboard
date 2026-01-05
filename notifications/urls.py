from django.urls import path
from .views import notifications_view

urlpatterns = [
    path("", notifications_view, name="notifications"),
]
