from django.urls import path
from .views import RegisterView, FCMTokenView

urlpatterns = [
    path('', RegisterView.as_view(), name='register'),
    path('me/fcm/', FCMTokenView.as_view(), name='user_fcm_token'),
]
