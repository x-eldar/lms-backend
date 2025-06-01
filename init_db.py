import os
import random
from django.core.management import execute_from_command_line
from django.conf import settings
from faker import Faker
from datetime import datetime, timedelta

# Инициализация Faker для генерации случайных данных
fake = Faker('ru_RU')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Настройки базы данных
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')

args = ['manage.py', 'migrate']

# Настройка Django
settings.configure(
    INSTALLED_APPS=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'rest_framework',
        'corsheaders',
        'api',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': DB_PORT,
        }
    },
    AUTH_USER_MODEL='api.User',

    LANGUAGE_CODE = 'en-us',
    TIME_ZONE = 'Europe/Moscow',
    USE_I18N = True,
    USE_L10N = True,
    USE_TZ = True,

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
)

# Применяем миграции
execute_from_command_line(args)

from api.models import User, Post, Comment, Like
from django.contrib.auth.hashers import make_password

# Проверяем флаг для создания тестовых данных
CREATE_TEST_DATA = os.environ.get('CREATE_TEST_DATA', 'false').lower() == 'true'

if CREATE_TEST_DATA:
    print("Создание тестовых данных...")

    # Список российских городов
    CITIES = [
        'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань',
        'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону'
    ]

    # Создаем 15 пользователей с реальными данными
    users = []
    for i in range(7):
        try:
            gender = random.choice(['M', 'F'])
            first_name = fake.first_name_male() if gender == 'M' else fake.first_name_female()
            last_name = fake.last_name_male() if gender == 'M' else fake.last_name_female()

            user = User.objects.create(
                username=fake.unique.user_name(),
                email=fake.unique.email(),
                first_name=first_name,
                last_name=last_name,
                password=make_password('password123'),
                age=random.randint(18, 65),
                city=random.choice(CITIES),
                gender=gender,
            )
            users.append(user)
            print(f"Создан пользователь: {user.username} ({user.first_name} {user.last_name}, {user.city})")
        except Exception as e:
            print(f"Ошибка создания пользователя: {e}")
            continue

    # Создаем посты (от 2 до 7 на каждого пользователя)
    posts = []
    for user in users:
        num_posts = random.randint(1, 2)
        for _ in range(num_posts):
            # Генерируем случайную дату в пределах последних 2 лет
            random_days = random.randint(0, 730)  # 2 года в днях
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            random_seconds = random.randint(0, 59)

            created_at = datetime.now() - timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes,
                seconds=random_seconds
            )

            post = Post.objects.create(
                author=user,
                title=fake.sentence(nb_words=6),
                content='\n'.join(fake.paragraphs(nb=3)),
                created_at=created_at,
                updated_at=created_at
            )
            posts.append(post)
            print(f"Создан пост от {created_at.strftime('%Y-%m-%d %H:%M')}: {post.title[:50]}... (автор: {user.username})")

    # Создаем комментарии (от 1 до 5 на каждый пост)
    for post in posts:
        num_comments = random.randint(1, 5)
        comment_authors = random.sample(users, min(num_comments, len(users)))

        for author in comment_authors:
            try:
                Comment.objects.create(
                    post=post,
                    author=author,
                    text=fake.paragraph(nb_sentences=2),
                )
                print(f"Добавлен комментарий к посту {post.id} от {author.username}")
            except Exception as e:
                print(f"Ошибка создания комментария: {e}")

    # Добавляем лайки (уникальные пары пользователь-пост)
    like_records = 0
    for user in users:
        # Каждый пользователь лайкает от 5 до 15 случайных постов
        posts_to_like = random.sample(posts, min(random.randint(5, 15), len(posts)))

        for post in posts_to_like:
            try:
                # Используем get_or_create для избежания дубликатов
                _, created = Like.objects.get_or_create(
                    user=user,
                    post=post
                )
                if created:
                    like_records += 1
                    print(f"Лайк от {user.username} посту {post.id}")
            except Exception as e:
                print(f"Ошибка создания лайка: {e}")

    print(f"Тестовые данные успешно созданы! "
          f"Пользователей: {len(users)}, "
          f"Постов: {len(posts)}, "
          f"Комментариев: {Comment.objects.count()}, "
          f"Лайков: {like_records}")
else:
    print("CREATE_TEST_DATA не установлен, пропускаем создание тестовых данных")
