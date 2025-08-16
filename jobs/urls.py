from django.urls import path
from .views import (
    JobListView,
    JobDetailView,
    JobCreateView,
    JobUpdateView,
    JobDeleteView,
    apply_job,
    MyAppliedJobsView,
    MyPostedJobsView
)

# Define URL patterns for job views
urlpatterns = [
    # URL pattern for listing jobs
    path('', JobListView.as_view(), name='job-list'),
    # URL pattern for displaying job details
    path('job/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    # URL pattern for creating new job
    path('job/new/', JobCreateView.as_view(), name='job-create'),
    # URL pattern for updating job details
    path('job/<int:pk>/update/', JobUpdateView.as_view(), name='job-update'),
    # URL pattern for deleting job
    path('job/<int:pk>/delete/', JobDeleteView.as_view(), name='job-delete'),
    # URL pattern for applying to a job
    path('job/<int:pk>/apply/', apply_job, name='apply-job'),
    # URL pattern for displaying user's applied jobs
    path('my-applications/', MyAppliedJobsView.as_view(), name='my-applied-jobs'),
    # URL pattern for displaying user's posted jobs
    path('my-posted-jobs/', MyPostedJobsView.as_view(), name='my-posted-jobs'),
]
