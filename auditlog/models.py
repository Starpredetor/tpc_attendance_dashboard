from django.conf import settings
from django.db import models

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("CREATE", "Create"),
        ("UPDATE", "Update"),
        ("DELETE", "Delete"),
        ("ATTENDANCE", "Attendance"),
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("SYSTEM", "System"),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()

    target_type = models.CharField(max_length=100, blank=True, null=True)
    target_id = models.PositiveIntegerField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action_type} by {self.actor} @ {self.timestamp}"
