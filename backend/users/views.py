from rest_framework import generics, permissions
from .serializers import UserCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class RegisterView(generics.CreateAPIView):
	serializer_class = UserCreateSerializer
	permission_classes = [permissions.AllowAny]


class FCMTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get('fcm_token')
        if not token:
            return Response({'detail': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        user.fcm_token = token
        user.save()
        return Response({'status': 'ok'})
