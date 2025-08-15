from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Registration URLs
    path('register/', views.register, name='register'),
    path('register/choose-role/', views.choose_role, name='choose-role'),
    path('register/company/', views.register_company, name='register-company'),
    path('register/applicant/', views.register_applicant, name='register-applicant'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile-show'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    path('profile/<str:username>/', views.profile_view, name='profile-show-user'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/employer/', views.employer_dashboard, name='employer-dashboard'),
    path('dashboard/jobseeker/', views.jobseeker_dashboard, name='jobseeker-dashboard'),
]