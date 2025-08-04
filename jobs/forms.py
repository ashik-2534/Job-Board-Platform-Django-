from django import forms
from django.utils import timezone
from .models import Job, Application 

# job lsiting form using model form
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        exclude = ['posted_by', 'date_posted', 'is_active']
        widgets = {
            "description": forms.Textarea(attrs={'rows':4}),
            "requirements": forms.Textarea(attrs={'rows':4}),\
            "application_deadline": forms.DateTimeInput(attrs={'type': 'date'}),
        }
        
    def clean_application_deadline(self):
        deadline = self.cleaned_data.get('application_deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline
        
# application form for applicant
class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Application
        exclude = ['applicant', 'job', 'date_applied']
        widgets = {
            "cover_letter": forms.Textarea(attrs={'rows':4}),
        }