from django.db import models
from lectures.models import Lecture
from accounts.models import User
from students.models import Student


class AttendanceRecord(models.Model):

    STATUS_CHOICES = [("P", "Present"), ("A", "Absent")]

    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("lecture", "student")

