from django.conf import settings
from django.db import models


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student"
    )
    university = models.CharField(max_length=255)
    department = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.university})"
