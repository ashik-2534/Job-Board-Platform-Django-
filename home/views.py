from django.shortcuts import render
from django.contrib.auth.models import User
from jobs.models import Job
from users.models import Profile

def home(request):
    context = {
        'total_jobs': Job.objects.filter(is_active=True).count(),
        'total_companies': Profile.objects.filter(role='company').count(),
        'total_applicants': Profile.objects.filter(role='applicant').count(),
        'job_types': [
            {'name': 'Technology', 'code': 'tech', 'icon': 'fa-laptop-code', 'count': Job.objects.filter(is_active=True, job_type='FT').count()},
            {'name': 'Healthcare', 'code': 'health', 'icon': 'fa-heartbeat', 'count': Job.objects.filter(is_active=True, job_type='PT').count()},
            {'name': 'Finance', 'code': 'finance', 'icon': 'fa-chart-line', 'count': Job.objects.filter(is_active=True, job_type='CT').count()},
            {'name': 'Education', 'code': 'education', 'icon': 'fa-graduation-cap', 'count': Job.objects.filter(is_active=True, job_type='IN').count()},
        ]
    }
    return render(request, 'home/home.html', context)