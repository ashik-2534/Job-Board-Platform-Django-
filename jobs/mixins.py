# jobs/mixins.py
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class CompanyRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, 'profile') and self.request.user.profile.is_company

class ApplicantRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, 'profile') and self.request.user.profile.is_applicant
class CompanyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "profile") or request.user.profile.role != "company":
            messages.error(request, "Only companies can perform this action.")
            return render(request, "jobs/denied.html")
        return super().dispatch(request, *args, **kwargs)
