from django.urls import path
from users import views as user_views
from django.contrib.auth import views as auth_views
    
urlpatterns = [
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='job-list'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
]
