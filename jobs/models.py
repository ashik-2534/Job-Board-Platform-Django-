from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError


# Model to store information for job listing
class Job(models.Model):
    """
    Job model to store job details.
    """
    JOB_TYPES = [
        ("full-time", "Full-Time"),
        ("part-time", "Part-Time"),
        ("remote", "Remote"),
        ("contract", "Contract"),
    ]

    INDUSTRIES = [
        ("tech", "Technology"),
        ("finance", "Finance"),
        ("healthcare", "Healthcare"),
        ("education", "Education"),
        # Add more industries as needed
    ]

    EXPERIENCE_LEVELS = [
        ("entry", "Entry Level"),
        ("mid", "Mid Level"),
        ("senior", "Senior Level"),
    ]

    title = models.CharField(max_length=255)  # Job title
    company = models.CharField(max_length=255)  # Company name
    description = models.TextField()  # Job description
    location = models.CharField(max_length=150)  # Job location
    requirements = models.TextField()  # Job requirements
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default="full-time")  # Job type
    industry = models.CharField(max_length=50, choices=INDUSTRIES, default="tech")  # Industry
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default="entry")  # Experience level
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)  # User who posted the job
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Minimum salary
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Maximum salary
    salary = models.CharField(max_length=150, default="Nagotiable")  # Salary
    currency = models.CharField(max_length=10, default='BDT')  # Currency
    date_posted = models.DateTimeField(auto_now_add=True)  # Date posted
    application_deadline = models.DateTimeField(blank=True, null=True)  # Application deadline
    is_active = models.BooleanField(default=True)  # Is job active

    def __str__(self):
        """
        Returns a string representation of the job.
        """
        return f"{self.title} at {self.company}"

    def get_absolute_url(self):
        """
        Returns the absolute URL of the job.
        """
        return reverse("job-detail", kwargs={"pk": self.pk})


def validate_resume(value):
    """
    Validates the resume file.
    """
    if not value.name.endswith((".pdf", ".doc", ".docx")):
        raise ValidationError("Resume must be a PDF or Word document.")
    if value.size > 2 * 1024 * 1024:  # 2MB limit
        raise ValidationError("Resume file too large (max 2MB).")


class Application(models.Model):
    """
    Application model to store job application details.
    """
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")  # Job applied for
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)  # Applicant
    full_name = models.CharField(max_length=255)  # Applicant full name
    email = models.EmailField()  # Applicant email
    portfolio = models.URLField(max_length=200, blank=True, null=True)  # Applicant portfolio
    resume = models.FileField(upload_to="resumes/", default="resumes/sample_resume.pdf", validators=[validate_resume])  # Applicant resume
    cover_letter = models.TextField()  # Cover letter
    date_applied = models.DateTimeField(auto_now_add=True)  # Date applied

    def __str__(self):
        """
        Returns a string representation of the application.
        """
        return f"Application for {self.job.title} by {self.applicant.username}"

    class Meta:
        unique_together = ("job", "applicant")  # Ensure unique applications for a job by applicant

