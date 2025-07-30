from django.urls import path
from users import views as user_views
from django.contrib.auth import views as auth_views
from . import views
    
urlpatterns = [
    #login , logout & register
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='job-list'), name='logout'),
    #profile urls
    path('profile/', views.profile_view, name='profile-show'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    path('@<str:username>/', views.profile_view, name='profile-show-user'),
    # Dashboard URLs
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/employer/', views.employer_dashboard, name='employer-dashboard'),
    path('dashboard/jobseeker/', views.jobseeker_dashboard, name='jobseeker-dashboard')
]
