from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Job, Application
from .forms import JobForm, ApplicantForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


# View for job listings
class JobListView(ListView):
    model = Job
    template_name = "jobs/job_list.html"
    paginate_by = 10
    ordering = ["-date_posted"]

    def get_queryset(self):
        # Return only active jobs, ordered by the date posted
        return Job.objects.filter(is_active=True).order_by("-date_posted")


# View for job details
class JobDetailView(DetailView):
    model = Job
    # template_name = 'jobs/job_detail.html'


# View for creating a job, requires login
class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"
    success_url = reverse_lazy("my-jobs")

    def dispatch(self, request, *args, **kwargs):
        if (
            not hasattr(request.user, "profile")
            or request.user.profile.role != "company"
        ):
            messages.error(request, "Only companies can post jobs.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Associate the job with the currently logged-in user
        form.instance.posted_by = self.request.user
        return super().form_valid(form)


# View for updating a job, requires login and ownership
class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    form_class = JobForm
    success_url = reverse_lazy("my-jobs")

    def test_func(self):
        # Ensure that the current user is the one who posted the job
        job = self.get_object()
        return self.request.user == job.posted_by


# View for deleting a job, requires login and ownership
class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    success_url = reverse_lazy("job-list")

    def test_func(self):
        # Ensure that the current user is the one who posted the job
        job = self.get_object()
        return self.request.user == job.posted_by


# Function-based view for applying to a job
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == "POST":
        form = ApplicantForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the application with the associated job and applicant
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted!")
            return redirect("job-detail", pk=job.pk)
    else:
        form = ApplicantForm()
    context = {"form": form, "job": job}
    return render(request, "jobs/apply_job.html", context)


# View for listing jobs posted by the current user
class MyJobsListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = "jobs/my_jobs.html"
    context_object_name = "jobs"

    def get_queryset(self):
        # Return jobs posted by the current user, ordered by the date posted
        return Job.objects.filter(posted_by=self.request.user).order_by("-date_posted")
