from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet, RoutineViewSet, ReminderViewSet, MoodLogViewSet, 
    InsightViewSet, UserViewSet, AIGenerateScheduleView, 
    MusicProviderConnectView, MusicProviderCallbackView, SmartPromptView, set_music_mode,
    MemoryViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'routines', RoutineViewSet, basename='routine')
router.register(r'reminders', ReminderViewSet, basename='reminder')
router.register(r'mood', MoodLogViewSet, basename='mood')
router.register(r'insights', InsightViewSet, basename='insight')
router.register(r'users', UserViewSet, basename='user')
router.register(r'memories', MemoryViewSet, basename='memory')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', include('users.urls')),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('ai/generate-schedule/', AIGenerateScheduleView.as_view(), name='ai_generate_schedule'),
    path('music/connect/', MusicProviderConnectView.as_view(), name='music_connect'),
    path('music/callback/<str:provider>/', MusicProviderCallbackView.as_view(), name='music_callback'),
    path('ai/smart-prompts/', SmartPromptView.as_view(), name='smart_prompts'),
    path('music/<str:provider>/mode', set_music_mode, name='set_music_mode'),
]
