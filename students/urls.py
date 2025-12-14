# lectures/urls.py
from django.urls import path
from .views import student_profile

urlpatterns = [
    path("student/<int:student_id>/profile/", student_profile, name="student_profile"),
]
