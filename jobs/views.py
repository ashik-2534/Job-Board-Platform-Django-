from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .mixins import CompanyRequiredMixin
from .models import Job, Application
from .forms import JobForm, ApplicantForm
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q


# View for job listings
class JobListView(ListView):
    model = Job
    template_name = "jobs/job_list.html"
    paginate_by = 10
    ordering = ["-date_posted"]
    context_object_name = "object_list"

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True).order_by("-date_posted")

        # Get the search query from the URL parameter 'q'
        query = self.request.GET.get("q")
        if query:
            # Filter by title, company, or location containing the query
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(company__icontains=query)
                | Q(location__icontains=query)
            )
        return queryset


# View for job details
class JobDetailView(DetailView):
    model = Job
    # template_name = 'jobs/job_detail.html'


# View for creating a job, requires login
class JobCreateView(LoginRequiredMixin, CompanyRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = "jobs/job_form.html"
    success_url = reverse_lazy("my-posted-jobs")

    def form_valid(self, form):
        # Associate the job with the currently logged-in user
        form.instance.posted_by = self.request.user
        return super().form_valid(form)


# View for updating a job, requires login and ownership
class JobUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, CompanyRequiredMixin, UpdateView
):
    model = Job
    form_class = JobForm
    success_url = reverse_lazy("my-jobs")

    def test_func(self):
        # Ensure that the current user is the one who posted the job
        job = self.get_object()
        return self.request.user == job.posted_by


# View for deleting a job, requires login and ownership
class JobDeleteView(
    LoginRequiredMixin, UserPassesTestMixin, CompanyRequiredMixin, DeleteView
):
    model = Job
    success_url = reverse_lazy("job-list")

    def test_func(self):
        # Ensure that the current user is the one who posted the job
        job = self.get_object()
        return self.request.user == job.posted_by


# Function-based view for applying to a job
def apply_job(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.user.profile.role != "applicant":
        messages.error(request, "Only applicants can apply for jobs.")
        return redirect("job-detail", pk=job.pk)

    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect("job-detail", pk=job.pk)

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
"""class MyJobsListView(LoginRequiredMixin, ListView):
    model = Job
    context_object_name = "jobs"

    def dispatch(self, request, *args, **kwargs):

        if not hasattr(request.user, "profile"):
            messages.error(
                request,
                "Your account does not have a profile. Please complete your profile first.",
            )
            return redirect("register")

        if request.user.profile.role == "company":
            self.context_object_name = "posted_jobs"
            self.template_name = "jobs/my_posted_jobs.html"
        elif request.user.profile.role == "applicant":
            self.context_object_name = "applied_jobs"
            self.template_name = "jobs/my_applied_jobs.html"
        else:
            messages.error(request, "Your role does not permit viewing this page.")
            return redirect("job-list")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Return jobs posted by the current user, ordered by the date posted
        if self.request.user.profile.role == "company":
            return Job.objects.filter(posted_by=self.request.user).order_by(
                "-date_posted"
            )
        elif self.request.user.profile.role == "applicant":
            return (
                Job.objects.filter(applications__applicant=self.request.user)
                .order_by("-applications__date_applied")
                .distinct()
            )
        return Job.objects.none()"""


class MyAppliedJobsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Application
    template_name = "jobs/my_applied_jobs.html"
    context_object_name = "applications" 
    paginate_by = 10

    def test_func(self):
        # Ensure the user is an applicant
        return (
            hasattr(self.request.user, "profile")
            and self.request.user.profile.role == "applicant"
        )

    def get_queryset(self):
        return (
            Application.objects.filter(applicant=self.request.user)
            .select_related("job")
            .order_by("-date_applied")
        )


class MyPostedJobsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Job
    template_name = "jobs/my_posted_jobs.html"
    context_object_name = "posted_jobs"
    paginate_by = 10

    def test_func(self):
        # Ensure the user is a company/employer
        return (
            hasattr(self.request.user, "profile")
            and self.request.user.profile.role == "company"
        )

    def get_queryset(self):
        # This annotates each job with the number of applications it has received.
        return (
            Job.objects.filter(posted_by=self.request.user)
            .annotate(application_count=Count("applications"))
            .order_by("-date_posted")
        )
