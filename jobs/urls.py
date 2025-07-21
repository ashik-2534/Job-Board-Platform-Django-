from django.urls import path
from .views import (
    JobListView,
    JobDetailView,
    JobCreateView,
    JobUpdateView,
    JobDeleteView,
    apply_job,
    MyJobsListView,
)

urlpatterns = [
    path('', JobListView.as_view(), name='job-list'),
    path('job/<int:pk>/', JobDetailView.as_view(), name='job-detail'),
    path('job/new/', JobCreateView.as_view(), name='job-create'),
    path('job/<int:pk>/update/', JobUpdateView.as_view(), name='job-update'),
    path('job/<int:pk>/delete/', JobDeleteView.as_view(), name='job-delete'),
    path('job/<int:pk>/apply/', apply_job.as_view(), name='apply-job'),
    path('my-jobs/', MyJobsListView.as_view(), name='my-jobs'),
]