from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Routine(models.Model):
    """
    A routine represents a collection of tasks that are performed regularly.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    frequency = models.CharField(max_length=50)  # daily, weekly, custom
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Task(models.Model):
    """
    A task represents a single actionable item that needs to be completed.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        IN_PROGRESS = 'in_progress', _('In Progress')
        DONE = 'done', _('Done')
        SKIPPED = 'skipped', _('Skipped')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    routine = models.ForeignKey(Routine, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    priority = models.IntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Reminder(models.Model):
    """
    A reminder is associated with a task and triggers notifications.
    """
    class Type(models.TextChoices):
        GENTLE = 'gentle', _('Gentle')
        URGENT = 'urgent', _('Urgent')
        ADAPTIVE = 'adaptive', _('Adaptive')

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='reminders')
    trigger_time = models.DateTimeField()
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.GENTLE)
    message = models.TextField(blank=True)
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder for {self.task.title}"


class MoodLog(models.Model):
    """
    Tracks user's mood and energy levels throughout the day.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mood_level = models.IntegerField()  # Scale of 1-10
    energy_level = models.IntegerField()  # Scale of 1-10
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mood log for {self.user.username} at {self.timestamp}"


class Insight(models.Model):
    """
    Stores analytics and insights about user's task completion and patterns.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    completion_rate = models.FloatField()
    total_tasks = models.IntegerField()
    completed_tasks = models.IntegerField()
    focus_time = models.DurationField()
    streak_days = models.IntegerField(default=0)
    metrics = models.JSONField(default=dict)  # For storing additional metrics
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"Insights for {self.user.username} on {self.date}"


class Memory(models.Model):
    """
    Stores conversation history and context for the AI assistant.
    Implements semantic memory using vector embeddings for context-aware responses.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    role = models.CharField(max_length=20, choices=[
        ('user', _('User')),
        ('assistant', _('Assistant')),
        ('system', _('System'))
    ])
    context = models.JSONField(default=dict)  # Stores emotion, task context, etc.
    vector_embedding = models.JSONField(null=True, blank=True)  # For semantic search
    relevance_score = models.FloatField(default=1.0)  # For memory importance/decay
    timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Memories'
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['user', 'role']),
        ]

    def __str__(self):
        return f"{self.role} message from {self.user.username} at {self.timestamp}"
