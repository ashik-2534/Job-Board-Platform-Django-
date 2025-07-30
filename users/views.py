from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from jobs.models import Job, Application

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_view(request, username=None):
    """Display user profile - can view own or others' profiles"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get or create profile if it doesn't exist
    profile, created = Profile.objects.get_or_create(user=user)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': user == request.user
    }
    
    return render(request, 'users/profile_show.html', context)


@login_required
def profile_edit(request):
    """Edit current user's profile"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile-show')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    
    return render(request, 'users/profile_edit.html', context)

@login_required
def dashboard_view(request):
    """
    Main dashboard view that redirects to appropriate dashboard based on user role
    """
    if not hasattr(request.user, 'profile'):
        messages.error(request, 'Please complete your profile first.')
        return redirect('profile')
    
    if request.user.profile.role == 'company':
        return redirect('employer-dashboard')
    elif request.user.profile.role == 'applicant':
        return redirect('jobseeker-dashboard')
    else:
        messages.error(request, 'Invalid user role.')
        return redirect('job-list')

@login_required
def employer_dashboard(request):
    """
    Dashboard for employers/companies
    """
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'company':
        messages.error(request, 'Access denied. This page is for employers only.')
        return redirect('job-list')
    
    # Get posted jobs
    posted_jobs = Job.objects.filter(posted_by=request.user).order_by('-date_posted')
    
    # Calculate statistics
    total_jobs = posted_jobs.count()
    active_jobs = posted_jobs.filter(is_active=True).count()
    inactive_jobs = total_jobs - active_jobs
    
    # Recent jobs (last 5)
    recent_jobs = posted_jobs[:5]
    
    # Total applications received
    total_applications = Application.objects.filter(job__posted_by=request.user).count()
    
    # Recent applications (last 10)
    recent_applications = Application.objects.filter(
        job__posted_by=request.user
    ).select_related('job', 'applicant').order_by('-date_applied')[:10]
    
    # Applications in last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    recent_applications_count = Application.objects.filter(
        job__posted_by=request.user,
        date_applied__gte=week_ago
    ).count()
    
    # Jobs with most applications
    popular_jobs = posted_jobs.annotate(
        application_count=Count('applications')
    ).order_by('-application_count')[:5]
    
    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'inactive_jobs': inactive_jobs,
        'total_applications': total_applications,
        'recent_applications_count': recent_applications_count,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'popular_jobs': popular_jobs,
    }
    
    return render(request, 'dashboard/employer_dashboard.html', context)

@login_required
def jobseeker_dashboard(request):
    """
    Dashboard for job seekers/applicants
    """
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'applicant':
        messages.error(request, 'Access denied. This page is for job seekers only.')
        return redirect('job-list')
    
    # Get user's applications
    user_applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-date_applied')
    
    # Calculate statistics
    total_applications = user_applications.count()
    
    # Recent applications (last 5)
    recent_applications = user_applications[:5]
    
    # Applications in last 7 days
    week_ago = timezone.now() - timedelta(days=7)
    recent_applications_count = user_applications.filter(
        date_applied__gte=week_ago
    ).count()
    
    # Get recommended jobs (active jobs not applied to)
    applied_job_ids = user_applications.values_list('job_id', flat=True)
    recommended_jobs = Job.objects.filter(
        is_active=True
    ).exclude(
        id__in=applied_job_ids
    ).order_by('-date_posted')[:5]
    
    # Get recently posted jobs (last 7 days)
    recent_job_posts = Job.objects.filter(
        is_active=True,
        date_posted__gte=week_ago
    ).exclude(
        id__in=applied_job_ids
    ).order_by('-date_posted')[:5]
    
    context = {
        'total_applications': total_applications,
        'recent_applications_count': recent_applications_count,
        'recent_applications': recent_applications,
        'recommended_jobs': recommended_jobs,
        'recent_job_posts': recent_job_posts,
    }
    
    return render(request, 'dashboard/jobseeker_dashboard.html', context)