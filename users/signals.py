# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update user profile when a User instance is saved.
    Combines both create and save operations for efficiency.
    """
    if created:
        try:
            # Check if profile already exists (edge case handling)
            profile, was_created = Profile.objects.get_or_create(
                user=instance,
                defaults={
                    'role': getattr(instance, '_profile_role', 'applicant')
                }
            )
            if was_created:
                logger.info(f"Profile created for user: {instance.username}")
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.username}: {str(e)}")
    else:
        # Only save profile if it exists and the save didn't originate from the profile
        if hasattr(instance, 'profile') and not kwargs.get('update_fields'):
            try:
                instance.profile.save()
            except Exception as e:
                logger.error(f"Error saving profile for user {instance.username}: {str(e)}")