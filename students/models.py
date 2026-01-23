from django.db import models
from lectures.models import Batch



class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Branches"

    def __str__(self):
        return self.name


class Student(models.Model):

    full_name = models.CharField(max_length=255, db_index=True)
    roll_number = models.CharField(max_length=8, unique=True, db_index=True)  # format r'^(23|24|25)[A-Z]{2}\d{4}$'
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, db_index=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    email = models.EmailField(unique=True, db_index=True)
    contact_number = models.CharField(max_length=15)

    
    parent_contact_number = models.CharField(max_length=15)
    parent_email = models.EmailField()


    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['batch', 'is_active']),
            models.Index(fields=['roll_number', 'is_active']),
        ]

    def __str__(self):
        return f"{self.full_name}- ({self.roll_number})"
    
