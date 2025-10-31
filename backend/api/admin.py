from django.contrib import admin
from .models import Task, Routine, Reminder, MoodLog, Insight


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'user', 'status', 'start_time')
	list_filter = ('status',)
	search_fields = ('title', 'description')


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'user', 'frequency')
	search_fields = ('name',)


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
	list_display = ('id', 'task', 'trigger_time', 'type', 'is_sent')


@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'mood_level', 'energy_level', 'timestamp')


@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'date', 'completion_rate')
