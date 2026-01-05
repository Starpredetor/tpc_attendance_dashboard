from django.contrib import admin
from django.contrib import admin
from .models import Batch, Lecture

from lectures.models import Batch, Lecture


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)



@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "batch",
        "date",
        "lecture_type",
    )
    list_filter = ("batch", "lecture_type", "date")
    search_fields = ("title",)
    ordering = ("-date",)

