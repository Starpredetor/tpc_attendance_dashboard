from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "roll_number",
        "full_name",
        "branch",
        "batch",
        "slot",
        "email",
        "is_active",
    )
    list_filter = ("branch", "batch", "slot", "is_active")
    search_fields = ("roll_number", "full_name", "email")
    ordering = ("roll_number",)

    fieldsets = (
        ("Student Info", {
            "fields": ("roll_number", "full_name", "branch", "batch", "slot")
        }),
        ("Contact Info", {
            "fields": ("email", "contact_number")
        }),
        ("Parent Info", {
            "fields": ("parent_email", "parent_contact_number")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
    )