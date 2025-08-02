# assistant/urls.py
from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('', views.AssistantView.as_view(), name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/feedback/', views.feedback_api, name='feedback_api'),
    path('api/history/', views.chat_history_api, name='history_api'),
    path('api/suggestions/', views.suggestions_api, name='suggestions_api'),
]