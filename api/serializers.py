from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Like, User, Post, Comment
from rest_framework_simplejwt.tokens import RefreshToken

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя с дополнительными полями"""
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'posts_count', 'age', 'city', 'gender']
        read_only_fields = ['id', 'posts_count']

    def get_posts_count(self, obj):
        if hasattr(obj, 'posts') and obj.posts is not None:
            return obj.posts.count()
        return 0

class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для поста с расширенной информацией"""
    author = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'title', 'content',
            'created_at', 'updated_at', 'likes_count',
            'comments_count', 'is_liked'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['user', 'created_at']
        read_only_fields = ['user', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post_title = serializers.CharField(source='post.title', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'post_title', 'author', 'text', 'created_at']
        read_only_fields = ['author', 'post', 'created_at']

class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа"""
    username = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            if not user:
                msg = 'Неверные учетные данные'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Необходимо указать имя пользователя и пароль'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации пользователя"""
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2',
                 'first_name', 'last_name', 'age', 'city', 'gender', 'tokens']
        read_only_fields = ['tokens']

    def get_tokens(self, obj):
        refresh = RefreshToken.for_user(obj)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value.lower()

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают")

        required_fields = ['first_name', 'last_name', 'age', 'city', 'gender']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError({field: "Это поле обязательно"})

        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age'],
            city=validated_data['city'],
            gender=validated_data['gender']
        )
        return user
