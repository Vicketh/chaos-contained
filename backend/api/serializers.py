from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Task, Routine, Reminder, MoodLog, Insight, Memory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'wake_time', 'preferences', 'focus_music')
        read_only_fields = ('id',)


class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class MoodLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodLog
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')


class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class MemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Memory
        fields = '__all__'
        read_only_fields = ('id', 'timestamp', 'vector_embedding')


class SmartPromptSerializer(serializers.Serializer):
    input_text = serializers.CharField(required=True)
    context = serializers.JSONField(required=False, default=dict)
    task_id = serializers.IntegerField(required=False, allow_null=True)
    

class MusicConnectSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=['spotify', 'apple', 'youtube'])
    code = serializers.CharField(required=False)  # Only required for callback
    state = serializers.CharField(required=False)  # For CSRF protection
    auth_url = serializers.URLField(read_only=True)  # Return URL to frontend

    def create(self, validated_data):
        raise NotImplementedError("Use views directly")

    def update(self, instance, validated_data):
        raise NotImplementedError("Use views directly")
