import os
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from api.models import Routine, Reminder, MoodLog
from api.serializers import SmartPromptSerializer

User = get_user_model()

class SmartPromptEngine:
    """
    Background AI task monitor for user activity and smart prompts.
    """
    def __init__(self, user):
        self.user = user

    def get_prompts(self):
        prompts = []
        now = timezone.now()
        # Example: Missed routines
        missed = Routine.objects.filter(user=self.user, completed=False, time__lt=now.time())
        for routine in missed:
            prompts.append({
                'message': f"You missed your routine: {routine.title}",
                'action_type': None,
                'action_data': None,
                'timestamp': now,
            })
        # Example: Missed reminders
        reminders = Reminder.objects.filter(user=self.user, completed=False, time__lt=now.time())
        for reminder in reminders:
            prompts.append({
                'message': f"Reminder: {reminder.title}",
                'action_type': None,
                'action_data': None,
                'timestamp': now,
            })
        # Example: Suggest a walk if inactive
        last_mood = MoodLog.objects.filter(user=self.user).order_by('-timestamp').first()
        if last_mood and (now - last_mood.timestamp).total_seconds() > 2*60*60:
            prompts.append({
                'message': "Take a short walk — you've been inactive for 2 hours.",
                'action_type': 'walk',
                'action_data': None,
                'timestamp': now,
            })
        # Example: WhatsApp Bible study
        # (Assume user has a routine with 'bible study' in title and a contact field)
        bible_study = Routine.objects.filter(user=self.user, title__icontains='bible study').first()
        if bible_study and bible_study.time.weekday() == now.weekday():
            prompts.append({
                'message': "It's time for your Bible study — open WhatsApp?",
                'action_type': 'whatsapp',
                'action_data': bible_study.contact if hasattr(bible_study, 'contact') else None,
                'timestamp': now,
            })
        return prompts

    def suggest_new_habits(self):
        # Example: If user misses a routine 3+ times, suggest a new time
        missed = Routine.objects.filter(user=self.user, completed=False)
        for routine in missed:
            if routine.missed_count >= 3:
                yield {
                    'message': f"You often miss {routine.title}. Try a different time?",
                    'action_type': None,
                    'action_data': None,
                    'timestamp': timezone.now(),
                }

# Usage: (to be run as a periodic task or management command)
def run_smart_prompt_engine():
    for user in User.objects.all():
        engine = SmartPromptEngine(user)
        prompts = engine.get_prompts()
        # Save or send prompts to user (e.g., via API, notification, or DB)
        # ...
