from rest_framework import viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import httpx
from .models import Task, Routine, Reminder, MoodLog, Insight, Memory
from .serializers import (
    TaskSerializer, RoutineSerializer, ReminderSerializer, MoodLogSerializer,
    InsightSerializer, UserSerializer, MusicConnectSerializer, MemorySerializer
)
from .ai_smart_prompt import SmartPromptEngine
import os
import openai
import secrets
from rest_framework.views import APIView
from rest_framework import status

openai.api_key = os.environ.get('OPENAI_API_KEY')


User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only to owner
        return hasattr(obj, 'user') and obj.user == request.user


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RoutineViewSet(viewsets.ModelViewSet):
    queryset = Routine.objects.all().order_by('-created_at')
    serializer_class = RoutineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all().order_by('-created_at')
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(task__user=self.request.user)


class MoodLogViewSet(viewsets.ModelViewSet):
    queryset = MoodLog.objects.all().order_by('-timestamp')
    serializer_class = MoodLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MoodLog.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InsightViewSet(viewsets.ModelViewSet):
    queryset = Insight.objects.all().order_by('-date')
    serializer_class = InsightSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Insight.objects.filter(user=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class AIGenerateScheduleView(APIView):
    """Generate an optimized schedule using OpenAI."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not openai.api_key:
            return Response({'detail': 'OpenAI API key not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class MusicProviderConnectView(APIView):
    """Handle OAuth flow for music service providers."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Start OAuth flow by returning auth URL."""
        serializer = MusicConnectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        provider = serializer.validated_data['provider']
        state = secrets.token_urlsafe(32)  # Generate CSRF token

        # Store state token with user session/cache for verification later
        request.session[f'oauth_state_{provider}'] = state

        auth_url = self._get_provider_auth_url(provider, state)
        return Response({
            'auth_url': auth_url,
            'state': state
        })

    def _get_provider_auth_url(self, provider, state):
        """Generate OAuth URL for specified provider."""
        base_urls = {
            'spotify': 'https://accounts.spotify.com/authorize',
            'youtube': 'https://accounts.google.com/o/oauth2/v2/auth',
            'apple': 'https://appleid.apple.com/auth/authorize'
        }

        # Get client ID from settings based on provider
        client_id = os.environ.get(f'{provider.upper()}_CLIENT_ID')
        if not client_id:
            raise ValueError(f'{provider} client ID not configured')

        params = {
            'spotify': {
                'client_id': client_id,
                'response_type': 'code',
                'redirect_uri': f'{os.environ.get("API_BASE_URL")}/api/music/callback/{provider}',
                'state': state,
                'scope': 'user-read-playback-state user-modify-playback-state'
            },
            'youtube': {
                'client_id': client_id,
                'response_type': 'code',
                'redirect_uri': f'{os.environ.get("API_BASE_URL")}/api/music/callback/{provider}',
                'state': state,
                'scope': 'https://www.googleapis.com/auth/youtube.force-ssl',
                'access_type': 'offline',
                'include_granted_scopes': 'true'
            },
            'apple': {
                'client_id': client_id,
                'response_type': 'code',
                'redirect_uri': f'{os.environ.get("API_BASE_URL")}/api/music/callback/{provider}',
                'state': state,
                'scope': 'music'
            }
        }

        from urllib.parse import urlencode
        return f"{base_urls[provider]}?{urlencode(params[provider])}"


class MusicProviderCallbackView(APIView):
    """Handle OAuth callback from music service providers."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, provider):
        """Handle OAuth callback with authorization code."""
        serializer = MusicConnectSerializer(data={
            'provider': provider,
            'code': request.GET.get('code'),
            'state': request.GET.get('state')
        })

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Verify state token to prevent CSRF
        stored_state = request.session.get(f'oauth_state_{provider}')
        if not stored_state or stored_state != serializer.validated_data['state']:
            return Response({'detail': 'Invalid state token'}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange code for access token
        try:
            token_data = self._exchange_code_for_token(
                provider,
                serializer.validated_data['code']
            )

            # Store tokens securely with user
            request.user.music_tokens = {
                **request.user.music_tokens,
                provider: token_data
            }
            request.user.save()

            return Response({'status': 'success'})

        except Exception as e:
            return Response(
                {'detail': f'Token exchange failed: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _exchange_code_for_token(self, provider, code):
        """Exchange authorization code for access and refresh tokens."""
        import requests

        token_urls = {
            'spotify': 'https://accounts.spotify.com/api/token',
            'youtube': 'https://oauth2.googleapis.com/token',
            'apple': 'https://appleid.apple.com/auth/token'
        }

        client_id = os.environ.get(f'{provider.upper()}_CLIENT_ID')
        client_secret = os.environ.get(f'{provider.upper()}_CLIENT_SECRET')

        if not all([client_id, client_secret]):
            raise ValueError(f'{provider} client credentials not configured')

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': f'{os.environ.get("API_BASE_URL")}/api/music/callback/{provider}',
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = requests.post(token_urls[provider], data=data)
        response.raise_for_status()

        return response.json()

        tasks = request.data.get('tasks', [])
        wake_time = request.data.get('wake_time', None)
        prompt = f"Generate an optimized daily schedule given these tasks: {tasks} and wake_time: {wake_time}. Return JSON list of tasks with start_time and duration."

        try:
            resp = openai.ChatCompletion.create(
                model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.7,
                max_tokens=800,
            )
            content = resp['choices'][0]['message']['content']
            return Response({'result': content})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIChatView(APIView):
    """A simple conversational endpoint backed by OpenAI."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not openai.api_key:
            return Response({'detail': 'OpenAI API key not configured.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        message = request.data.get('message', '')
        try:
            resp = openai.ChatCompletion.create(
                model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[{'role': 'user', 'content': message}],
                temperature=0.9,
                max_tokens=500,
            )
            content = resp['choices'][0]['message']['content']
            return Response({'reply': content})
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MusicConnectView(APIView):
    """Initiate music provider OAuth flow (placeholder).
    This endpoint returns a provider-specific authorization URL the frontend can open.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, provider=None):
        provider = provider or request.query_params.get('provider')
        if provider not in ('spotify', 'apple', 'youtube'):
            return Response({'detail': 'Unsupported provider'}, status=status.HTTP_400_BAD_REQUEST)

        # Build provider URL based on env vars (placeholder)
        redirect_uri = os.environ.get('MUSIC_OAUTH_REDIRECT', 'https://your-backend.com/api/v1/music/callback/')
        if provider == 'spotify':
            client_id = os.environ.get('SPOTIFY_CLIENT_ID', '')
            scope = 'user-read-playback-state user-modify-playback-state'
            auth_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}"
            return Response({'auth_url': auth_url})
        # TODO: implement for other providers similarly
        return Response({'auth_url': redirect_uri})


class MusicCallbackView(APIView):
    """Callback endpoint to receive OAuth code and exchange for tokens. Store tokens in user's preferences (securely).
    Note: In production store tokens encrypted and consider server-side refresh handling.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, provider=None):
        # Expect provider and code in body
        provider = provider or request.data.get('provider')
        code = request.data.get('code')
        if not provider or not code:
            return Response({'detail': 'Missing provider or code'}, status=status.HTTP_400_BAD_REQUEST)
        # Placeholder: in production exchange code for tokens with provider's token endpoint
        # For now, just store the code in user's preferences to indicate connection
        user = request.user
        prefs = user.preferences or {}
        prefs.setdefault('music', {})[provider] = {'connected': True, 'code': code}
        user.preferences = prefs
        user.save()
        return Response({'detail': 'connected'})


class SmartPromptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        engine = SmartPromptEngine(request.user)
        prompts = engine.get_prompts()
        return Response(prompts)

    def post(self, request):
        message = request.data.get('message')
        # For now, echo or simple rule-based response
        if message:
            return Response({'reply': f"I'll remind you: {message}"})
        return Response({'reply': "Please enter a message."}, status=400)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def set_music_mode(request, provider):
    mode = request.data.get('mode')
    # Here you would integrate with the provider's API to set a playlist or mood
    # For now, just return success
    return Response({'status': 'ok', 'mode': mode})


class MemoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing conversation memories with vector-based semantic search."""

    queryset = Memory.objects.all().order_by('-timestamp')
    serializer_class = MemorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Filter memories by user and optionally by time range or relevance score."""
        queryset = Memory.objects.filter(user=self.request.user)

        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        # Filter by minimum relevance score
        min_relevance = self.request.query_params.get('min_relevance')
        if min_relevance:
            queryset = queryset.filter(relevance_score__gte=float(min_relevance))

        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)

        return queryset.order_by('-timestamp')

    def perform_create(self, serializer):
        """Save the memory with the current user."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def semantic_search(self, request):
        """Search memories using semantic similarity."""
        query = request.data.get('query')
        if not query:
            return Response(
                {'error': 'Query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Use FastAPI service for semantic search (blocking HTTP call)
        try:
            response = httpx.post(
                f"{settings.REALTIME_SERVICE_URL}/memory/search",
                json={
                    'user_id': request.user.id,
                    'query': query,
                    'limit': request.data.get('limit', 5)
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            memories = response.json()
            if response.status_code != 200:
                return Response(
                    {'error': 'Semantic search request failed', 'details': memories},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            return Response(memories)
        except Exception as e:
            return Response(
                {'error': f'Semantic search failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """Handle bulk create/update operations."""
        memories = request.data.get('memories', [])
        if not memories:
            return Response(
                {'error': 'No memories provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add user to each memory
        for memory in memories:
            memory['user'] = request.user.id

        serializer = self.get_serializer(data=memories, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'])
    def bulk_update(self, request):
        """Handle bulk updates."""
        memories = request.data.get('memories', [])
        if not memories:
            return Response(
                {'error': 'No memories provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify all memories belong to user
        memory_ids = [m['id'] for m in memories if 'id' in m]
        existing_memories = Memory.objects.filter(
            id__in=memory_ids,
            user=request.user
        )

        if len(existing_memories) != len(memory_ids):
            return Response(
                {'error': 'Some memories not found or not owned by user'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update memories
        updated_memories = []
        for memory_data in memories:
            memory = existing_memories.get(id=memory_data['id'])
            serializer = self.get_serializer(
                memory,
                data=memory_data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            updated_memories.append(serializer.data)

        return Response(updated_memories)

    @action(detail=False, methods=['delete'])
    def cleanup(self, request):
        """Remove old or low-relevance memories based on user preferences."""
        try:
            # Get retention days with null-safe access
            memory_prefs = request.user.preferences.get('memory', {})
            if not isinstance(memory_prefs, dict):
                memory_prefs = {}
            
            retention_days = memory_prefs.get('memory_retention_days', 30)
            min_relevance = memory_prefs.get('min_relevance_score', 0.5)
            
            # Normalize timestamps to seconds precision for deterministic comparison
            now = timezone.now().replace(microsecond=0)
            cutoff_date = now - timedelta(days=retention_days)
            
            print(f"DEBUG: Now: {now}")
            print(f"DEBUG: Cutoff date: {cutoff_date}")
            print(f"DEBUG: Min relevance score: {min_relevance}")
            
            # Debug all memories first
            all_memories = Memory.objects.filter(user=request.user)
            print(f"DEBUG: All memories: {[f'{m.timestamp}, score={m.relevance_score}' for m in all_memories]}")
            
            from django.db.models import Q
            old_memories = Memory.objects.filter(
                user=request.user
            ).filter(
                # Use lte for inclusive comparison at second precision
                Q(timestamp__lte=cutoff_date) | Q(relevance_score__lt=min_relevance)
            )
            print(f"DEBUG: Old memories to delete: {[f'{m.timestamp}, score={m.relevance_score}' for m in old_memories]}")
            print(f"DEBUG: Query SQL: {str(old_memories.query)}")
            deleted_count = old_memories.delete()[0]

            return Response({
                'message': f'Deleted {deleted_count} old memories',
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date.isoformat()
            })
        except Exception as e:
            return Response(
                {'error': f'Memory cleanup failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
