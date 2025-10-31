from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2')
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class VoicePreferencesSerializer(serializers.Serializer):
    enabled = serializers.BooleanField(default=True)
    useHeadphones = serializers.BooleanField(default=False)
    volume = serializers.FloatField(min_value=0, max_value=1, default=0.75)
    speed = serializers.FloatField(min_value=0.5, max_value=2.0, default=1.0)
    voice_id = serializers.CharField(default='default')
    background_enabled = serializers.BooleanField(default=True)
    background_volume = serializers.FloatField(min_value=0, max_value=1, default=0.3)


class MemoryPreferencesSerializer(serializers.Serializer):
    context_window = serializers.IntegerField(min_value=1, max_value=50, default=10)
    memory_retention_days = serializers.IntegerField(min_value=1, max_value=365, default=30)
    include_emotions = serializers.BooleanField(default=True)
    save_voice_clips = serializers.BooleanField(default=False)
    personalization_level = serializers.ChoiceField(
        choices=['minimal', 'balanced', 'high'],
        default='balanced'
    )


class NotificationPreferencesSerializer(serializers.Serializer):
    voice_enabled = serializers.BooleanField(default=True)
    text_enabled = serializers.BooleanField(default=True)
    quiet_hours_start = serializers.TimeField(default='22:00')
    quiet_hours_end = serializers.TimeField(default='07:00')


class UserPreferencesSerializer(serializers.Serializer):
    voice = VoicePreferencesSerializer(required=False)
    memory = MemoryPreferencesSerializer(required=False)
    notifications = NotificationPreferencesSerializer(required=False)

    def validate(self, data):
        if not any(data.values()):
            raise serializers.ValidationError("At least one preference category must be provided")
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    preferences = UserPreferencesSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'wake_time', 'preferences', 'focus_music', 'timezone')
        read_only_fields = ('id',)

    def validate_preferences(self, value):
        serializer = UserPreferencesSerializer(data=value)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
