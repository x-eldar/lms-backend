from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from .models import Post, Comment, User, Like
from .serializers import (
    PostSerializer,
    CommentSerializer,
    UserSerializer,
    LoginSerializer,
    UserRegisterSerializer
)

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для постов (CRUD + лайки)"""
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = User.objects.get(id=self.request.user.id)
        serializer.save(author=user)

    def get_serializer_context(self):
        """Переопределён для передачи объекта request в сериализатор"""
        return {'request': self.request}

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = User.objects.get(id=self.request.user.id)

        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete()
            return Response({'status': 'unliked', 'likes_count': post.post_likes.count(), 'is_liked': False})

        return Response({'status': 'liked', 'likes_count': post.post_likes.count(), 'is_liked': True})


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()  # Добавляем этот атрибут
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_pk')
        if post_id:
            post = Post.objects.get(pk=post_id)
            print(post)
            return Comment.objects.filter(post=post).order_by('created_at')
        return Comment.objects.none()

    def perform_create(self, serializer):
        user = User.objects.get(id=self.request.user.id)
        post_id = self.kwargs.get('post_pk')
        post = Post.objects.get(pk=post_id)
        serializer.save(
                author=user,
                post=post
            )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Получение данных текущего пользователя"""
        user = User.objects.get(id=self.request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class LoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({"detail": "Неверные учетные данные"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = UserSerializer(serializer.user).data

        return Response({
            **user_data,
            "tokens": {
                "refresh": serializer.validated_data["refresh"],
                "access": serializer.validated_data["access"]
            }
        })

class RefreshTokenView(TokenRefreshView):
    """View для обновления токена"""
    pass

class LogoutView(APIView):
    """View для выхода из системы"""

    def post(self, request):
        logout(request)
        return Response({'status': 'success'})

class RegisterView(APIView):
    """View для регистрации пользователя"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view

@api_view(['GET'])
def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username__iexact=username).exists()
    return Response({'available': not exists})

@api_view(['GET'])
def check_email(request):
    email = request.GET.get('email', '').lower()
    exists = User.objects.filter(email__iexact=email).exists()
    return Response({'available': not exists})
