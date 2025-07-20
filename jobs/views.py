from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,                                              #generic views
    UpdateView,
    DeleteView,
)
from .models import Job, Application  # models 
from .forms import JobForm, ApplicantForm # forms
from django.urls import reverse_lazy
from django.contrib import messages 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# view of Job listing 
class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    paginate_by = 10
    ordering = ['-date_posted']
    
    def get_queryset(self):
        return Job.objects.filter(is_active=True).order_by('-date_posted')
    
class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    
class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job 
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    
    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)
    
