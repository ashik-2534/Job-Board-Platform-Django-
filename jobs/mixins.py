# jobs/mixins.py
from django.contrib import messages
from django.shortcuts import redirect, render

class CompanyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.profile.role != "company":
            messages.error(request, "Only companies can perform this action.")
            return render(request, "jobs/denied.html")
        return super().dispatch(request, *args, **kwargs)
