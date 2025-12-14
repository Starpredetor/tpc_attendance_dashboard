from django.db import models
from lectures.models import Lecture
from students.models import Student
from django.conf import settings



class AttendanceRecord(models.Model):

    STATUS_CHOICES = [("P", "Present"), ("A", "Absent")]

    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ("lecture", "student")


    def __str__(self):
        return f"{self.student.roll_number} - {self.lecture} : {self.status}"


class EODAttendanceRun(models.Model):
    run_date = models.DateField(unique=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"EOD Attendance Run - {self.run_date}"
