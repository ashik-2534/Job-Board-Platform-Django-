# chatbot/urls.py
"""
URL configuration for the chatbot app.

Contains URLs for the chatbot API, chat history, and session clearing.
"""
from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    # Chatbot API endpoint
    path("api/chat/", views.ChatbotAPIView.as_view(), name="chat-api"),
    # Get chat history
    path("api/history/", views.get_chat_history, name="chat-history"),
    # Clear chat session
    path("api/clear/", views.clear_chat_session, name="clear-session"),
]
