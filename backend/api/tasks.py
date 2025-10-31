import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from django.utils import timezone
from api.models import Routine, Reminder
from users.models import User

# Initialize Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_ADMIN_CREDENTIALS)
firebase_admin.initialize_app(cred)

def send_notification(user_id, title, body, data=None):
    """Send FCM notification to a specific user."""
    try:
        user = User.objects.get(id=user_id)
        if not user.fcm_token:
            return False

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=user.fcm_token,
        )
        
        messaging.send(message)
        return True
    except Exception as e:
        print(f"Failed to send notification: {e}")
        return False

def check_and_notify_routines():
    """Check for upcoming routines and send notifications."""
    now = timezone.now()
    # Get routines due in the next 5 minutes
    soon = now + timezone.timedelta(minutes=5)
    routines = Routine.objects.filter(
        time__gte=now.time(),
        time__lt=soon.time(),
        active=True
    )

    for routine in routines:
        send_notification(
            user_id=routine.user_id,
            title="Routine Reminder",
            body=f"Time for: {routine.title}",
            data={
                "type": "routine",
                "id": str(routine.id),
            }
        )

def check_and_notify_reminders():
    """Check for upcoming reminders and send notifications."""
    now = timezone.now()
    # Get reminders due in the next 5 minutes
    soon = now + timezone.timedelta(minutes=5)
    reminders = Reminder.objects.filter(
        time__gte=now,
        time__lt=soon,
        completed=False
    )

    for reminder in reminders:
        send_notification(
            user_id=reminder.task.user_id,
            title="Task Reminder",
            body=reminder.title or f"Reminder for: {reminder.task.title}",
            data={
                "type": "reminder",
                "id": str(reminder.id),
                "task_id": str(reminder.task.id),
            }
        )

def check_smart_prompts():
    """Check and notify users about smart prompts."""
    from api.ai_smart_prompt import SmartPromptEngine
    
    for user in User.objects.filter(is_active=True):
        engine = SmartPromptEngine(user)
        prompts = engine.get_prompts()
        
        for prompt in prompts:
            send_notification(
                user_id=user.id,
                title="Smart Suggestion",
                body=prompt['message'],
                data={
                    "type": "smart_prompt",
                    "action_type": prompt.get('action_type'),
                    "action_data": prompt.get('action_data'),
                }
            )