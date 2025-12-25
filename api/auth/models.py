import hashlib
import hmac

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Менеджер пользователя с поддержкой регистрации по Telegram без пароля."""

    def _get_telegram_secret(self):
        secret = getattr(settings, "TELEGRAM_AUTH_SECRET", None)
        if not secret:
            raise ValueError("TELEGRAM_AUTH_SECRET is not set in settings")
        return secret

    def _build_tg_token(self, tg_id):
        secret = self._get_telegram_secret()
        msg = str(tg_id).encode()
        return hmac.new(secret.encode(), msg, hashlib.sha256).hexdigest()

    def _normalize_username(self, username, tg_id=None, tg_username=None):
        if username:
            return self.model.normalize_username(username)
        if tg_username:
            return self.model.normalize_username(tg_username)
        if tg_id:
            return f"tg_{tg_id}"
        raise ValueError("Username or tg_id is required")

    def _create_user(self, username=None, password=None, tg_id=None, tg_username=None, tg_token=None, **extra_fields):
        username = self._normalize_username(username, tg_id=tg_id, tg_username=tg_username)
        token = tg_token or (self._build_tg_token(tg_id) if tg_id else None)
        user = self.model(username=username, tg_id=tg_id, tg_username=tg_username, tg_token=token, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, username=None, password=None, tg_id=None, tg_username=None, tg_token=None, **extra_fields):
        """Регистрация обычного пользователя; пароль не обязателен (Telegram)."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            username,
            password,
            tg_id=tg_id,
            tg_username=tg_username,
            tg_token=tg_token,
            **extra_fields,
        )

    def create_from_telegram(self, tg_id, tg_username=None, phone=None, tg_token=None, **extra_fields):
        """Создать пользователя через Telegram Mini App без пароля, с HMAC-токеном."""
        if not tg_id:
            raise ValueError("tg_id is required for Telegram sign-up")
        extra_fields.setdefault("phone", phone)
        token = tg_token or self._build_tg_token(tg_id)
        return self.create_user(tg_id=tg_id, tg_username=tg_username, tg_token=token, **extra_fields)

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, password, **extra_fields)

    def authenticate_user(self, username, password):
        """Удобный хелпер для авторизации через стандартный authenticate."""
        from django.contrib.auth import authenticate

        return authenticate(username=username, password=password)

    def authenticate_by_tg_token(self, tg_token):
        """Авторизация по заранее сгенерированному HMAC-токену."""
        if not tg_token:
            return None
        try:
            return self.get(tg_token=tg_token)
        except self.model.DoesNotExist:
            return None


class CustomUser(AbstractUser):
    tg_username = models.CharField(verbose_name="Telegram username", max_length=150, blank=True, null=True, unique=True)
    tg_id = models.BigIntegerField(verbose_name="Telegram id", blank=True, null=True, unique=True)
    tg_token = models.CharField(verbose_name="Telegram token", max_length=128, blank=True, null=True, unique=True)
    phone = models.CharField(verbose_name="Номер телефона", max_length=32, blank=True, null=True, unique=True)
    email = models.EmailField(verbose_name="Email", blank=True, null=True, unique=True)
    first_name = models.CharField(verbose_name="Имя", max_length=150, blank=True, null=True)
    second_name = models.CharField(verbose_name="Фамилия", max_length=150, blank=True, null=True)
    avatar = models.ImageField(verbose_name="Аватарка", upload_to="images/avatars", blank=True, null=True)
    admin = models.BooleanField(verbose_name="Роль администратора", default=False)
    moderator = models.BooleanField(verbose_name="Роль модератора", default=False)
    banned = models.BooleanField(verbose_name="Заблокирован", default=False)

    objects = CustomUserManager()

    REQUIRED_FIELDS = []  # пароль не обязателен при Telegram-регистрации

    def __str__(self):
        return self.username


class ApproveRequest(models.Model):
    class RequestType(models.IntegerChoices):
        DRIVER = 1, "Водитель"
        CAR = 2, "Автомобиль"
        PASSPORT = 3, "Паспорт"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="approval_requests")
    date_time = models.DateTimeField(verbose_name="Дата и время заявки", default=timezone.now)
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Модератор", related_name="reviewed_requests")
    request_type = models.IntegerField(verbose_name="Тип запроса", choices=RequestType.choices, null=True)
    comment = models.TextField(verbose_name="Комментарий модератора", blank=True, null=True)
    approved = models.BooleanField(verbose_name="Подтверждено", default=False)

    def __str__(self):
        return f"Запрос {self.id} от {self.user}"


class ApproveImages(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    request = models.ForeignKey(ApproveRequest, on_delete=models.CASCADE, verbose_name="Заявка", related_name="images")
    image = models.ImageField(verbose_name="Фотография", upload_to="images/approve")

    def __str__(self):
        return f"Фото для заявки {self.request_id}"


class Passport(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    number = models.CharField(verbose_name="Номер", max_length=20, blank=True, null=True)
    series = models.CharField(verbose_name="Серия", max_length=10, blank=True, null=True)

    def __str__(self):
        return f"Паспорт {self.user}"


class Car(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="cars")
    car_brand = models.CharField(verbose_name="Марка автомобиля", max_length=50, blank=True, null=True)
    car_model = models.CharField(verbose_name="Модель автомобиля", max_length=50, blank=True, null=True)
    car_year = models.CharField(verbose_name="Год автомобиля", max_length=4, blank=True, null=True)
    car_color = models.CharField(verbose_name="Цвет автомобиля", max_length=30, blank=True, null=True)
    car_country = models.CharField(verbose_name="Страна, где авто на учете", max_length=50, blank=True, null=True)
    car_number = models.CharField(verbose_name="Номер автомобиля", max_length=16, blank=True, null=True)
    approved = models.BooleanField(verbose_name="подтверждено", default=False)
    image = models.ImageField(verbose_name="Фотография", upload_to="images/cars", blank=True, null=True)

    def __str__(self):
        return f"{self.car_brand} {self.car_model} ({self.car_number})"


class Driver(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", related_name="driver_profile")
    rating = models.PositiveIntegerField(verbose_name="Рейтинг", default=0)
    approved = models.BooleanField(verbose_name="Подтвержден", default=True)

    def __str__(self):
        return f"Водитель {self.user}"
