from django.db import models
from django.contrib.auth.models import User



# model to store information for job listing 
class Job (models.Model):
    JOB_TYPES = [
        ('FT', 'Full-time'),
        ('PT', 'Part-time'),
        ('CN', 'Contract'),
        ('RM', 'Remote'),
    ]
    
    title = models.CharField(max_length=255)
    company = models.CharField(max_length = 255)
    description = models.TextField()
    location = models.CharField(max_length = 150)
    requirements = models.TextField()
    job_type = models.CharField(max_length=2, choices=JOB_TYPES)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    salary = models.CharField(max_length = 150, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    application_deadline  = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.name} at {self.company}'
    
    
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length = 255)
    email = models.EmailField()
    portfolio = models.URLField(max_length = 200)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField()
    date_applied = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.username}"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
