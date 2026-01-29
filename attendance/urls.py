from django.urls import path
from .views import (
    admin_attendance_list,
    mark_attendance,
    mark_absent,
    batch_analysis_index,
    batch_attendance_analysis,
)

urlpatterns = [
    path("admin_view/", admin_attendance_list, name="admin_attendance_list"),
    path("admin_view/batch-analysis/", batch_analysis_index, name="batch_analysis_index"),
    path(
        "admin_view/batch-analysis/<int:batch_id>/",
        batch_attendance_analysis,
        name="batch_attendance_analysis",
    ),
    path("attendance/mark/", mark_attendance, name="mark_attendance"),
    path("mark-absent/<int:lecture_id>/", mark_absent, name="mark-absent"),

]
