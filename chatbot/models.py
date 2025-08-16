# chatbot/models.py
from django.db import models
from django.contrib.auth.models import User


class ChatSession(models.Model):
    """
    Model representing a chat session.

    Attributes:
        user (ForeignKey): The user who started the chat session. Can be null for anonymous users.
        session_id (CharField): The unique identifier for the chat session.
        created_at (DateTimeField): The date and time when the chat session was created.
        updated_at (DateTimeField): The date and time when the chat session was last updated.
        is_active (BooleanField): Indicates whether the chat session is currently active.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        """
        Returns a string representation of the chat session.

        Returns:
            str: A string in the format "Chat Session {session_id} - {user or 'Anonymous'}"
        """
        return f"Chat Session {self.session_id} - {self.user or 'Anonymous'}"


class ChatMessage(models.Model):
    """
    Model representing a message in a chat session.

    Attributes:
        session (ForeignKey): The chat session this message belongs to.
        message_type (CharField): The type of the message (user, bot, system).
        content (TextField): The content of the message.
        metadata (JSONField): Additional metadata for the message.
        created_at (DateTimeField): The date and time when the message was created.
    """
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('system', 'System'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        """
        Returns a string representation of the chat message.

        Returns:
            str: A string in the format "{message_type}: {content[:50]}..."
        """
        return f"{self.message_type}: {self.content[:50]}..."
