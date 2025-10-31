from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'fcm_token')
	search_fields = ('email', 'username')
	list_filter = ('is_staff', 'is_superuser')
