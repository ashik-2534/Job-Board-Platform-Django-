# assistant/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
import uuid
from .models import ChatSession, ChatMessage, AIFeedback
from .services import JobBoardAssistant


class AssistantView(View):
    """Main assistant page view"""
    
    def get(self, request):
        assistant = JobBoardAssistant()
        suggestions = assistant.get_quick_suggestions(request.user)
        
        context = {
            'suggestions': suggestions,
            'user_role': getattr(request.user.profile, 'role', 'visitor') if request.user.is_authenticated else 'visitor'
        }
        return render(request, 'assistant/chat.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """API endpoint for chat messages"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get or create session
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session, created = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={
                'user': request.user if request.user.is_authenticated else None,
                'is_active': True
            }
        )
        
        # Get AI response
        assistant = JobBoardAssistant()
        ai_result = assistant.get_ai_response(message, request.user, session_id)
        
        # Save message and response
        chat_message = ChatMessage.objects.create(
            session=session,
            message=message,
            response=ai_result['response'],
            message_type=ai_result['message_type']
        )
        
        # Get new suggestions after response
        suggestions = assistant.get_quick_suggestions(request.user)
        
        return JsonResponse({
            'response': ai_result['response'],
            'session_id': session_id,
            'message_id': chat_message.id,
            'suggestions': suggestions,
            'success': ai_result['success']
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Something went wrong'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def feedback_api(request):
    """API endpoint for user feedback"""
    try:
        data = json.loads(request.body)
        message_id = data.get('message_id')
        is_helpful = data.get('is_helpful')
        feedback_text = data.get('feedback_text', '')
        
        if not message_id or is_helpful is None:
            return JsonResponse({'error': 'message_id and is_helpful are required'}, status=400)
        
        try:
            message = ChatMessage.objects.get(id=message_id)
        except ChatMessage.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
        
        # Create or update feedback
        feedback, created = AIFeedback.objects.get_or_create(
            message=message,
            user=request.user if request.user.is_authenticated else None,
            defaults={
                'is_helpful': is_helpful,
                'feedback_text': feedback_text
            }
        )
        
        if not created:
            feedback.is_helpful = is_helpful
            feedback.feedback_text = feedback_text
            feedback.save()
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Something went wrong'}, status=500)


@require_http_methods(["GET"])
def chat_history_api(request):
    """API endpoint to get chat history"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        return JsonResponse({'error': 'session_id is required'}, status=400)
    
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.order_by('timestamp')
        
        history = []
        for msg in messages:
            history.append({
                'id': msg.id,
                'message': msg.message,
                'response': msg.response,
                'timestamp': msg.timestamp.isoformat(),
                'message_type': msg.message_type
            })
        
        return JsonResponse({'history': history})
        
    except ChatSession.DoesNotExist:
        return JsonResponse({'history': []})
    except Exception as e:
        return JsonResponse({'error': 'Something went wrong'}, status=500)


@require_http_methods(["GET"])
def suggestions_api(request):
    """API endpoint to get quick suggestions"""
    assistant = JobBoardAssistant()
    suggestions = assistant.get_quick_suggestions(request.user)
    
    return JsonResponse({'suggestions': suggestions})