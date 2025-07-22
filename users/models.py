from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = [
        ("company", "Company"),
        ("applicant", "Applicant"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="applicant")

    def __str__(self):
        return f"{self.user.username} Profile"
