# assistant/admin.py
from django.contrib import admin
from .models import ChatSession, ChatMessage, AIFeedback


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__username']
    readonly_fields = ['session_id', 'created_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'timestamp', 'get_user']
    list_filter = ['message_type', 'timestamp']
    search_fields = ['message', 'response']
    readonly_fields = ['timestamp']
    
    def get_user(self, obj):
        return obj.session.user.username if obj.session.user else 'Anonymous'
    get_user.short_description = 'User'


@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['feedback_text', 'user__username']
    readonly_fields = ['created_at']