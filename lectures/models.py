from django.db import models
from django.core.exceptions import ValidationError
from datetime import date
from django.conf import settings




class Batch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Batches"
    
    def __str__(self):
        return self.name
    

class Lecture(models.Model):

    LECTURE_TYPE_CHOICES = [("MS", "Morning Session"), ("AS", "Afternoon Session")]

    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, db_index=True)
    date = models.DateField(db_index=True)
    title = models.CharField(max_length=200)
    lecture_type = models.CharField(max_length=2, choices=LECTURE_TYPE_CHOICES, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("batch", "date", "lecture_type")
        indexes = [
            models.Index(fields=['date', 'batch']),
            models.Index(fields=['batch', 'date', 'lecture_type']),
        ]

    def __str__(self):
        return f"{self.title} ({self.date} {self.batch.name} {self.lecture_type})"