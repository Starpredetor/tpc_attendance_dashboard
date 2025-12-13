from django.db import models
from accounts.models import User

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("OVERRIDE", "Override"),
        ("LOGIN", "Login"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
    )

    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)

    message = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.model_name} - {self.object_id}"