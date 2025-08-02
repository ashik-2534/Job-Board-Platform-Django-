# assistant/services.py
import openai
import os
from django.conf import settings
from django.contrib.auth.models import User
from jobs.models import Job, Application
from users.models import Profile
from django.db.models import Q, Count
from datetime import datetime, timedelta
import json


class JobBoardAssistant:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def get_user_context(self, user):
        """Get relevant user context for personalized responses"""
        context = {
            'is_authenticated': user.is_authenticated,
            'role': None,
            'user_info': {}
        }
        
        if user.is_authenticated:
            try:
                profile = user.profile
                context['role'] = profile.role
                context['user_info'] = {
                    'username': user.username,
                    'role': profile.role,
                }
            except Profile.DoesNotExist:
                pass
        
        return context
    
    def search_jobs(self, query, user=None, limit=5):
        """Search jobs based on query and user profile"""
        jobs_query = Job.objects.filter(is_active=True)
        
        if query:
            jobs_query = jobs_query.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(requirements__icontains=query) |
                Q(company__icontains=query) |
                Q(location__icontains=query)
            )
        
        # If user is authenticated applicant, prioritize relevant jobs
        if user and user.is_authenticated:
            try:
                if user.profile.role == 'applicant':
                    # Get jobs user hasn't applied to
                    applied_job_ids = Application.objects.filter(
                        applicant=user
                    ).values_list('job_id', flat=True)
                    jobs_query = jobs_query.exclude(id__in=applied_job_ids)
            except Profile.DoesNotExist:
                pass
        
        return jobs_query.order_by('-date_posted')[:limit]
    
    def get_user_applications(self, user, limit=5):
        """Get user's recent applications"""
        if not user.is_authenticated:
            return []
        
        return Application.objects.filter(
            applicant=user
        ).order_by('-date_applied')[:limit]
    
    def get_posted_jobs(self, user, limit=5):
        """Get jobs posted by employer"""
        if not user.is_authenticated:
            return []
        
        return Job.objects.filter(
            posted_by=user
        ).order_by('-date_posted')[:limit]
    
    def get_site_statistics(self):
        """Get general site statistics"""
        return {
            'total_jobs': Job.objects.filter(is_active=True).count(),
            'total_applications': Application.objects.count(),
            'companies_count': User.objects.filter(profile__role='company').count(),
            'recent_jobs': Job.objects.filter(is_active=True).order_by('-date_posted')[:3]
        }
    
    def classify_message_type(self, message, user_role):
        """Classify the type of user message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['job', 'position', 'work', 'career', 'hiring']):
            if user_role == 'company':
                return 'job_posting'
            else:
                return 'job_search'
        elif any(word in message_lower for word in ['profile', 'resume', 'cv', 'skills']):
            return 'profile_help'
        elif any(word in message_lower for word in ['apply', 'application', 'interview']):
            return 'application_tips'
        else:
            return 'general'
    
    def prepare_context_data(self, user, message, message_type):
        """Prepare relevant context data based on message type and user"""
        context_data = []
        user_context = self.get_user_context(user)
        
        # Add site statistics
        stats = self.get_site_statistics()
        context_data.append(f"Site Statistics: {stats['total_jobs']} active jobs, {stats['total_applications']} total applications")
        
        if message_type == 'job_search' and user_context['role'] == 'applicant':
            # Search for relevant jobs
            jobs = self.search_jobs(message, user)
            if jobs:
                context_data.append("Relevant Jobs:")
                for job in jobs:
                    context_data.append(f"- {job.title} at {job.company} ({job.location}) - {job.job_type}")
            
            # Add user's applications
            applications = self.get_user_applications(user)
            if applications:
                context_data.append("Your Recent Applications:")
                for app in applications:
                    context_data.append(f"- Applied to {app.job.title} at {app.job.company}")
        
        elif message_type == 'job_posting' and user_context['role'] == 'company':
            # Add employer's posted jobs
            posted_jobs = self.get_posted_jobs(user)
            if posted_jobs:
                context_data.append("Your Posted Jobs:")
                for job in posted_jobs:
                    app_count = job.applications.count()
                    context_data.append(f"- {job.title} ({app_count} applications)")
        
        elif message_type == 'general':
            # Add recent jobs for general queries
            recent_jobs = stats['recent_jobs']
            if recent_jobs:
                context_data.append("Recent Job Postings:")
                for job in recent_jobs:
                    context_data.append(f"- {job.title} at {job.company}")
        
        return "\n".join(context_data)
    
    def get_ai_response(self, message, user, session_id=None):
        """Get AI response based on user message and context"""
        try:
            user_context = self.get_user_context(user)
            message_type = self.classify_message_type(message, user_context.get('role'))
            context_data = self.prepare_context_data(user, message, message_type)
            
            # Create system prompt
            system_prompt = f"""
            You are an AI assistant for a job board platform. You help users with job searching, career advice, and platform navigation.
            
            IMPORTANT RULES:
            1. Only answer based on the provided job board data
            2. If you don't have specific information, guide users to relevant platform features
            3. Be helpful, friendly, and professional
            4. Provide actionable advice
            
            User Context:
            - Role: {user_context.get('role', 'visitor')}
            - Authenticated: {user_context['is_authenticated']}
            
            Platform Data:
            {context_data}
            
            Message Type: {message_type}
            """
            
            # Create user prompt
            user_prompt = f"""
            User message: {message}
            
            Please provide a helpful response based on the job board data provided. 
            Keep responses concise but informative.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return {
                'response': response.choices[0].message.content,
                'message_type': message_type,
                'success': True
            }
            
        except Exception as e:
            return {
                'response': "I'm sorry, I'm having trouble processing your request right now. Please try again later or contact support.",
                'message_type': 'general',
                'success': False,
                'error': str(e)
            }
    
    def get_quick_suggestions(self, user):
        """Get quick suggestion buttons based on user role"""
        user_context = self.get_user_context(user)
        
        if user_context['role'] == 'applicant':
            return [
                "Find jobs for me",
                "How to improve my profile?",
                "Application tips",
                "What jobs match my skills?"
            ]
        elif user_context['role'] == 'company':
            return [
                "How to write a good job post?",
                "Find qualified candidates",
                "Hiring best practices",
                "Review my job postings"
            ]
        else:
            return [
                "How does this platform work?",
                "Show me recent jobs",
                "How to create an account?",
                "Platform features"
            ]