from django.contrib import admin
from .models import AttendanceRecord

from attendance.models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    ist_display = (
        "student",
        "lecture",
        "status",
        "marked_by",
        "marked_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "lecture__date",
        "lecture__batch",
    )
    search_fields = (
        "student__roll_no",
        "student__full_name",
    )
    autocomplete_fields = ("student", "lecture")
    readonly_fields = ("student","lecture", "marked_by","marked_at","updated_at")

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete in Django admin
        return request.user.is_superuser
    