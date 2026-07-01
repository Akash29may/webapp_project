from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# 1. User Model (Supports both Teachers and Students)
class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    contact_no = models.CharField(max_length=15, blank=True, null=True)
    profile_img = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username