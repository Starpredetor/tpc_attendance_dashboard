from django.db import models
from django.conf import settings
from lectures.models import Lecture


class NotificationLog(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    date = models.DateField()
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("lecture", "date")
