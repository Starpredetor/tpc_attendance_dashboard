from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from django.conf import settings




class Batch(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    

class Lecture(models.Model):

    LECTURE_TYPE_CHOICES = [("MS", "Morning Session"), ("AS", "Afternoon Session")]

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    date = models.DateField()
    title = models.CharField(max_length=200)
    lecture_type = models.CharField(max_length=2, choices=LECTURE_TYPE_CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("batch", "date", "lecture_type")

    def __str__(self):
        return f"{self.title} ({self.date} {self.batch.name} {self.lecture_type})"