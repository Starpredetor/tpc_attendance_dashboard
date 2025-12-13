from django.db import models
from lectures.models import Batch, Slot


class Student(models.Model):

    BRANCH_CHOICES = [
        ('CE', 'Computer Engineering'),
        ('IT', 'Information Technology'),
        ('CB', 'Computer Science and Business Systems'),
        ('EC', 'Electronics and Communication Engineering'),
        ('ET', 'Electronics and Telecommunication Engineering'),
        ('AD', 'Artificial Intelligence and Data Science'),
        ('AM', 'Artificial Intelligence and Machine Learning'),
        ('CC', 'Cybersecurity'),
        ('MT', 'MBA-Tech'),
    ]

    full_name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=8, unique=True)  # format r'^(23|24|25)[A-Z]{2}\d{4}$'
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    branch = models.CharField(max_length=2, choices=BRANCH_CHOICES)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15)
    
    parent_contact_number = models.CharField(max_length=15)
    parent_email = models.EmailField()


    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.full_name}- ({self.roll_number})"
    
