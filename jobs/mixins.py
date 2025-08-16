
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import UserPassesTestMixin
# Custom mixin to restrict access to certain views to only companies
class CompanyRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, 'profile') and self.request.user.profile.is_company

# Custom mixin to restrict access to certain views to only applicants
class ApplicantRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, 'profile') and self.request.user.profile.is_applicant

# Custom mixin to restrict access to certain views to only companies.
# This mixin overrides the dispatch method to check if the user is a company and if not,
#   it displays an error message and redirects to the denied page.
class CompanyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "profile") or request.user.profile.role != "company":
            messages.error(request, "Only companies can perform this action.")
            return render(request, "jobs/denied.html")
        return super().dispatch(request, *args, **kwargs)

