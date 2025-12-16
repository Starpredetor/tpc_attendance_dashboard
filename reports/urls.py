from django.urls import path
from . import views


urlpatterns = [
    path("", views.reports_index, name="report"),
    path("student/", views.student_report_page, name="student_report_page"),
    path("lecture/", views.lecture_report_page, name="lecture_report_page"),

    path(
        "student/download/",
        views.student_attendance_report,
        name="student_attendance_report",
    ),
    path(
        "lecture/download/",
        views.lecture_attendance_report,
        name="lecture_attendance_report",
    ),
]