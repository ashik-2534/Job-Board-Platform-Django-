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
    # template_name = 'jobs/job_detail.html'
    
class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job 
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    
    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        return super().form_valid(form)
    
class JobUpdateView(UpdateView,LoginRequiredMixin, UserPassesTestMixin):
    model = Job
    form_class = JobForm
    
    def test_func(self):
        job = self.get_object()
        return self.request.user == job.posted_by # ensures only the user who posted can delete the job


class JobDeleteView(DeleteView, LoginRequiredMixin, UserPassesTestMixin):
    model = Job
    success_url = reverse_lazy('job-lsit')
    
    def test_func(self):
        job = self.get_object()
        return self.request.user == job.posted_by # ensures only the user who posted can delete the job
    

def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == "POST":
        form = ApplicantForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('job-detail', pk=pk)
    else:
        form = ApplicantForm()
    context = {
        'form':form, 
        'job': job,
    }
    return render ( request , 'jobs/apply_job.html',context )


class MyJobListView(LoginRequiredMixin,ListView):
    model = Job
    template_name = 'jobs/my_jobs.html'
    context_object_name = 'jobs'
    
    def get_queryset(self):
        return Job.objects.filter(posted_by = self.request.user).order_by('-date_posted')
    