from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Кастомная модель пользователя с аватаркой."""
    email = models.EmailField(_('email address'), unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    GENDER_CHOICES = [('M', 'Мужской'), ('F', 'Женский')]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    def __str__(self):
        return self.username

class Post(models.Model):
    """Модель поста с автором и лайками."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        User,
        through='Like',
        through_fields=('post', 'user'),
        related_name='liked_posts',
        blank=True  # Добавляем blank=True
    )

    def __str__(self):
        return self.title

class Comment(models.Model):
    """Модель комментария с автором."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author} on {self.post.title}'

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Один пользователь - один лайк на пост
