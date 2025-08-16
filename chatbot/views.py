# chatbot/views.py
import json
import uuid
from openai import OpenAI
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder

from .models import ChatSession, ChatMessage
from jobs.models import Job, Application
from users.models import Profile


# Set up OpenAI client
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key = settings.HF_API_KEY
)
class ChatbotContextBuilder:
    """Build context about the jobboard for the AI chatbot"""

    @staticmethod
    def get_platform_context():
        return """
        You are JobBoard AI Assistant, a helpful chatbot for a job board platform. Here's what you need to know:
        
        PLATFORM FEATURES:
        - Job posting and searching
        - User profiles (Companies and Job Seekers)
        - Job applications with resume uploads
        - Company profiles with detailed information
        - Job types: Full-time, Part-time, Contract, Remote
        
        USER ROLES:
        - Companies: Can post jobs, view applications, manage company profile
        - Applicants: Can search jobs, apply to jobs, manage applicant profile
        
        KEY FUNCTIONALITY:
        - Browse jobs by location, type, company
        - Apply to jobs with resume and cover letter
        - Companies can manage posted jobs and view applications
        - Profile management for both user types
        
        Be helpful, professional, and guide users through the platform features.
        """

    @staticmethod
    def get_user_context(user):
        if not user.is_authenticated:
            return "User is not logged in. They can browse jobs but need to register to apply."

        try:
            profile = user.profile
            context = f"User: {user.username} ({profile.get_role_display()})\n"

            if profile.is_company:
                job_count = Job.objects.filter(posted_by=user, is_active=True).count()
                context += f"Company: {profile.company_name or 'Not set'}\n"
                context += f"Active job postings: {job_count}\n"
                context += f"Industry: {profile.industry or 'Not specified'}\n"
            else:
                applied_count = Application.objects.filter(applicant=user).count()
                context += f"Applications submitted: {applied_count}\n"
                context += f"Experience: {profile.experience_years} years\n"
                context += f"Skills: {profile.skills or 'Not specified'}\n"

            return context
        except Profile.DoesNotExist:
            return f"User: {user.username} (No profile set up yet)"

    @staticmethod
    def get_recent_jobs_context(limit=5):
        recent_jobs = Job.objects.filter(is_active=True).order_by("-date_posted")[
            :limit
        ]
        if not recent_jobs:
            return "No active jobs currently posted."

        context = "Recent job postings:\n"
        for job in recent_jobs:
            context += f"- {job.title} at {job.company} ({job.get_job_type_display()}) - {job.location}\n"

        return context


@method_decorator(csrf_exempt, name="dispatch")
class ChatbotAPIView(View):
    """Main chatbot API endpoint"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get("message", "").strip()
            session_id = data.get("session_id")

            if not message:
                return JsonResponse({"error": "Message is required"}, status=400)

            # Get or create chat session
            if session_id:
                try:
                    session = ChatSession.objects.get(session_id=session_id)
                except ChatSession.DoesNotExist:
                    session = self._create_new_session(request.user)
            else:
                session = self._create_new_session(request.user)

            # Save user message
            ChatMessage.objects.create(
                session=session, message_type="user", content=message
            )

            # Generate AI response
            ai_response = self._generate_ai_response(message, session, request.user)

            # Save bot response
            ChatMessage.objects.create(
                session=session, message_type="bot", content=ai_response
            )

            return JsonResponse(
                {"response": ai_response, "session_id": session.session_id}
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

    def _create_new_session(self, user):
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        return ChatSession.objects.create(
            user=user if user.is_authenticated else None, session_id=session_id
        )

    def _generate_ai_response(self, message, session, user):
        """Generate AI response using OpenAI"""
        try:
            # Build context
            context_builder = ChatbotContextBuilder()
            system_context = context_builder.get_platform_context()
            user_context = context_builder.get_user_context(user)
            jobs_context = context_builder.get_recent_jobs_context()

            # Get recent conversation history
            recent_messages = session.messages.order_by('-created_at')[:10]
            conversation_history = []

            for msg in reversed(recent_messages):
                if msg.message_type == 'user':
                    conversation_history.append({"role": "user", "content": msg.content})
                elif msg.message_type == 'bot':
                    conversation_history.append({"role": "assistant", "content": msg.content})

            # Prepare messages for OpenAI
            messages = [
                {
                    "role": "system",
                    "content": f"{system_context}\n\nUSER CONTEXT:\n{user_context}\n\nCURRENT JOBS:\n{jobs_context}"
                }
            ]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": message})

            # Call OpenAI API
            response = client.responses.create(
                model="openai/gpt-oss-20b:fireworks-ai",
                input=messages,
                max_output_tokens=500,
                # temperature=0.7,
                store=True
            )
            

            return response.output_text

        except Exception as e:
            if "insufficient_quota" in str(e):
                    return "Our AI assistant is currently unavailable due to quota limits. Please try again later."

            return f"I'm sorry, I'm having trouble processing your request right now. Please try again later. Error: {str(e)}"


@require_http_methods(["GET"])
def get_chat_history(request):
    """Get chat history for a session"""
    session_id = request.GET.get("session_id")

    if not session_id:
        return JsonResponse({"error": "Session ID required"}, status=400)

    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all()

        history = []
        for message in messages:
            history.append(
                {
                    "type": message.message_type,
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                }
            )

        return JsonResponse({"history": history, "session_id": session.session_id})

    except ChatSession.DoesNotExist:
        return JsonResponse({"error": "Session not found"}, status=404)


@require_http_methods(["POST"])
@csrf_exempt
def clear_chat_session(request):
    """Clear/reset chat session"""
    try:
        data = json.loads(request.body)
        session_id = data.get("session_id")

        if session_id:
            ChatSession.objects.filter(session_id=session_id).update(is_active=False)

        return JsonResponse({"message": "Session cleared"})
    except:
        return JsonResponse({"error": "Failed to clear session"}, status=500)
