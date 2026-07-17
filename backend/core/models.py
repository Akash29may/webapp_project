from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user supporting both Teacher and Student roles."""

    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    profile_img = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    @property
    def role(self) -> str:
        if self.is_teacher:
            return "teacher"
        if self.is_student:
            return "student"
        return "none"

    def __str__(self) -> str:
        return self.username
