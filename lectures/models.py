from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from django.conf import settings

class Batch(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Slot(models.Model):
    name = models.CharField(max_length=255)
    date_ranges = models.JSONField(default=list)

    def clean(self):
        for r in self.date_ranges:
            if not isinstance(r, dict):
                raise ValidationError("Each date range must be an object")
            if "start" not in r or "end" not in r:
                raise ValidationError("Each range must contain start and end")
            try:
                s = date.fromisoformat(r["start"])
                e = date.fromisoformat(r["end"])
            except Exception:
                raise ValidationError("Dates must be in YYYY-MM-DD format")
            if s > e:
                raise ValidationError("Start date cannot be after end date")

    def __str__(self):
        return f"{self.name}"


class Lecture(models.Model):

    LECTURE_TYPE_CHOICES = [("MS", "Morning Session"), ("AS", "Afternoon Session")]

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    date = models.DateField()
    title = models.CharField(max_length=200)
    lecture_type = models.CharField(max_length=2, choices=LECTURE_TYPE_CHOICES)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("batch", "date", "lecture_type")

    def __str__(self):
        return f"{self.title} ({self.date})"