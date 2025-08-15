from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, HTML
class BaseUserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your email'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

class CompanyRegisterForm(BaseUserRegisterForm):
    company_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter company name'
    }))
    company_website = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://www.example.com'
    }))
    company_description = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Brief description of your company'
    }))
    
    class Meta(BaseUserRegisterForm.Meta):
            fields = BaseUserRegisterForm.Meta.fields + ['company_name', 'company_website', 'company_description']
        
    
    
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = Profile.objects.get(user=user)
            profile.role = 'company'
            profile.company_name = self.cleaned_data.get('company_name')
            profile.company_website = self.cleaned_data.get('company_website')
            profile.company_description = self.cleaned_data.get('company_description')
            profile.save()
        return user

class ApplicantRegisterForm(BaseUserRegisterForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last name'
    }))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone number'
    }))
    
    class Meta(BaseUserRegisterForm.Meta):
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'phone']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile = Profile.objects.get(user=user)
            profile.role = 'applicant'
            profile.phone = self.cleaned_data.get('phone', '')
            profile.save()
        return user

# Keep existing forms
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']
    
    def save(self, commit=True):
        user = super().save(commit)
        role = self.cleaned_data['role']
        Profile.objects.filter(user=user).update(role=role)
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

class CompanyProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'phone', 'bio', 'company_name', 'company_website', 
                 'company_description', 'company_size', 'industry']

class ApplicantProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'phone', 'bio', 'resume', 'skills', 
                 'experience_years', 'education']