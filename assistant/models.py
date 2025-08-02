# assistant/models.py
from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job


class ChatSession(models.Model):
    """Track chat sessions for users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Chat Session {self.session_id}"


class ChatMessage(models.Model):
    """Store chat messages for context and history"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=20, choices=[
        ('job_search', 'Job Search'),
        ('profile_help', 'Profile Help'),
        ('application_tips', 'Application Tips'),
        ('job_posting', 'Job Posting Help'),
        ('general', 'General Help'),
    ], default='general')
    
    def __str__(self):
        return f"Message in {self.session.session_id} at {self.timestamp}"


class AIFeedback(models.Model):
    """Track user feedback on AI responses"""
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_helpful = models.BooleanField()
    feedback_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for message {self.message.id}"