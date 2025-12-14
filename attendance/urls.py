from django.urls import path
from .views import admin_attendance_list, mark_attendance, mark_absent

urlpatterns = [
    path("admin_view/", admin_attendance_list, name="admin_attendance_list"),
    path("attendance/mark/", mark_attendance, name="mark_attendance"),
    path("mark-absent/<int:lecture_id>/", mark_absent, name="mark-absent"),

]
