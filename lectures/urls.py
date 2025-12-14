from django.urls import path
from .views import manage_lectures, edit_lecture, delete_lecture, create_lecture

urlpatterns = [
    path("", manage_lectures, name="manage_lectures"),
    path("create/", create_lecture, name="create_lecture"),
    path("edit/<int:lecture_id>/", edit_lecture, name="edit_lecture"),
    path("delete/<int:lecture_id>/", delete_lecture, name="delete_lecture"),
]
