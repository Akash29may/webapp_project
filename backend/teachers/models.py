from django.conf import settings
from django.db import models


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher"
    )
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.department})"
