"""
URL configuration for the home app.

Contains URLs for the home page.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
]
