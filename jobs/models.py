from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError


# model to store information for job listing
class Job(models.Model):
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

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=150)
    requirements = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default="full-time")
    industry = models.CharField(max_length=50, choices=INDUSTRIES, default="tech")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default="entry")
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    min_salary = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    max_salary = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    salary = models.CharField(max_length=150, default="Nagotiable")
    currency = models.CharField(max_length=10, default='BDT')
    date_posted = models.DateTimeField(auto_now_add=True)
    application_deadline = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_absolute_url(self):
        return reverse("job-detail", kwargs={"pk": self.pk})


def validate_resume(value):
    if not value.name.endswith((".pdf", ".doc", ".docx")):
        raise ValidationError("Resume must be a PDF or Word document.")
    if value.size > 2 * 1024 * 1024:  # 2MB limit
        raise ValidationError("Resume file too large (max 2MB).")


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    portfolio = models.URLField(max_length=200, blank=True, null=True)
    resume = models.FileField(
        upload_to="resumes/", default="resumes/sample_resume.pdf", validators=[validate_resume]
    )
    cover_letter = models.TextField()
    date_applied = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application for {self.job.title} by {self.applicant.username}"

    class Meta:
        unique_together = ("job", "applicant")
