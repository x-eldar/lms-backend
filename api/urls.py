from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet, UserViewSet, LoginView, LogoutView, RegisterView, UserViewSet, RefreshTokenView, check_email, check_username

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:post_pk>/comments/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='post-comments'),
    path('posts/<int:post_pk>/comments/<int:pk>/', CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comment-detail'),

    path('posts/<int:post_pk>/like/', PostViewSet.as_view({'post': 'like'}), name='post-like'),

    # JWT-TOKEN Authentication
    path('api/token/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),

    # Профиль
    path('profile/', UserViewSet.as_view({'get': 'me'}), name='profile'),

    path('api/check-username/', check_username),
    path('api/check-email/', check_email),
]
