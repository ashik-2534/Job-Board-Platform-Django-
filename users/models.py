from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Profile(models.Model):
    ROLE_CHOICES = [
        ("company", "Company"),
        ("applicant", "Applicant"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg", upload_to="profile_pics")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="applicant")
    
    # Common fields
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Company-specific fields
    company_name = models.CharField(max_length=100, blank=True)
    company_website = models.URLField(blank=True)
    company_description = models.TextField(blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    industry = models.CharField(max_length=100, blank=True)
    
    # Applicant-specific fields
    resume = models.FileField(upload_to='resumes/', blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated list of skills")
    experience_years = models.IntegerField(default=0)
    education = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} Profile ({self.get_role_display()})"
    
    def get_absolute_url(self):
        """Return the URL to this profile's public page"""
        return reverse('profile-show-user', kwargs={'username': self.user.username})
    
    @property
    def is_company(self):
        return self.role == 'company'
    
    @property
    def is_applicant(self):
        return self.role == 'applicant'