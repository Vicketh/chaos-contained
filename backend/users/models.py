from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model for Chaos Contained application.
    Extends Django's AbstractUser to add additional fields for user preferences and settings.
    """
    email = models.EmailField(_('email address'), unique=True)
    wake_time = models.TimeField(null=True, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    focus_music = models.JSONField(default=dict, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    fcm_token = models.CharField(max_length=256, blank=True, null=True)
    
    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Required for createsuperuser
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        return self.email
