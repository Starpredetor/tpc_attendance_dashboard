from django.db import models
from lectures.models import Lecture
from students.models import Student
from django.conf import settings



class AttendanceRecord(models.Model):

    STATUS_CHOICES = [("P", "Present"), ("A", "Absent")]

    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, db_index=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, db_index=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, db_index=True)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        unique_together = ("lecture", "student")
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['lecture', 'status']),
            models.Index(fields=['marked_at']),
        ]


    def __str__(self):
        return f"{self.student.roll_number} - {self.lecture} : {self.status}"


class EODAttendanceRun(models.Model):
    run_date = models.DateField(unique=True, db_index=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-run_date']
        verbose_name = "EOD Attendance Run"
        verbose_name_plural = "EOD Attendance Runs"

    def __str__(self):
        return f"EOD Attendance Run - {self.run_date}"
