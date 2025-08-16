# chatbot/admin.py
"""
Administrative interface for the chatbot models.

The ChatSessionAdmin and ChatMessageAdmin classes define the admin interface
for the ChatSession and ChatMessage models respectively.
"""

from django.contrib import admin
from .models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for the ChatSession model.
    """
    list_display = ('session_id', 'user', 'created_at', 'updated_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('session_id', 'user__username')
    readonly_fields = ('session_id', 'created_at', 'updated_at')
    
    # Select related user when retrieving chat sessions
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for the ChatMessage model.
    """
    list_display = ('session', 'message_type', 'content_preview', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('content', 'session__session_id')
    readonly_fields = ('created_at',)
    
    # Preview of the content of the message
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    # Select related session and user when retrieving chat messages
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('session', 'session__user')

