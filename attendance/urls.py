from django.urls import path
from .views import admin_attendance_list, mark_attendance

urlpatterns = [
    path("admin_view/", admin_attendance_list, name="admin_attendance_list"),
    path("attendance/mark/", mark_attendance, name="mark_attendance"),

]
