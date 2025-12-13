# lectures/urls.py
from django.urls import path
from .views import manage_lectures

urlpatterns = [
    path("", manage_lectures, name="manage_lectures"),
]
