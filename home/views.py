from django.shortcuts import render
from django.contrib.auth.models import User
from jobs.models import Job
from users.models import Profile


def home(request):
    """
    Render the home page with some basic statistics.

    Returns:
        HttpResponse: The rendered home page.
    """

    # Get the total number of active jobs and profiles
    total_jobs = Job.objects.filter(is_active=True).count()
    total_companies = Profile.objects.filter(role="company").count()
    total_applicants = Profile.objects.filter(role="applicant").count()

    # Get the count of jobs per industry
    job_types = [
        {
            "name": "Technology",
            "code": "tech",
            "icon": "fa-laptop-code",
            "count": Job.objects.filter(is_active=True, industry="tech").count(),
        },
        {
            "name": "Healthcare",
            "code": "health",
            "icon": "fa-heartbeat",
            "count": Job.objects.filter(is_active=True, industry="health").count(),
        },
        {
            "name": "Finance",
            "code": "finance",
            "icon": "fa-chart-line",
            "count": Job.objects.filter(is_active=True, industry="finance").count(),
        },
        {
            "name": "Education",
            "code": "education",
            "icon": "fa-graduation-cap",
            "count": Job.objects.filter(is_active=True, industry="education").count(),
        },
    ]

    # Render the home page with the statistics
    context = {
        "total_jobs": total_jobs,
        "total_companies": total_companies,
        "total_applicants": total_applicants,
        "job_types": job_types,
    }
    return render(request, "home/home.html", context)
