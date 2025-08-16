# chatbot/urls.py
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('api/chat/', views.ChatbotAPIView.as_view(), name='chat-api'),
    path('api/history/', views.get_chat_history, name='chat-history'),
    path('api/clear/', views.clear_chat_session, name='clear-session'),
]