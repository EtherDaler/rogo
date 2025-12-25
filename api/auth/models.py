import datetime

from django.db import models
from django.contrib.auth.models import User


class CustomUser(User):
    tg_username = models.CharField(verbose_name="Telegram username", null=True)
    tg_id = models.IntegerField(verbose_name="Telegram id", null=True)
    phone = models.CharField(verbose_name="Номер телефона", null=True)
    email = models.EmailField(verbose_name="Email", null=True)
    first_name = models.CharField(verbose_name="Имя", null=True)
    second_name = models.CharField(verbose_name="Фамилия", null=True)
    avatar = models.ImageField(verbose_name="Аватарка", null=True, upload_to="images/avatars")
    admin = models.BooleanField(verbose_name="Роль администратора", default=False)
    moderator = models.BooleanField(verbose_name="Роль модератора", default=False)
    banned = models.BooleanField(verbose_name="Заблокирован", default=False)


class ApproveRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    date_time = models.DateTimeField(verbose_name="Дата и время заявки", default=datetime.datetime.now())
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор")
    request_type = models.IntegerField(verbose_name="Тип запроса", null=True)
    comment = models.TextField(verbose_name="Комментарий модератора", null=True)
    approved = models.BooleanField(verbose_name="Подтверждено", default=False)


class ApproveImages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    request = models.ForeignKey(ApproveRequest, on_delete=models.CASCADE, verbose_name="Заявка")
    image = models.ImageField(verbose_name="Фотография", upload_to="images/approve")


class Passport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    number = models.CharField(verbose_name="Номер", null=True)
    series = models.CharField(verbose_name="Серия", null=True)


class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    car_brand = models.CharField(verbose_name="Марка автомобиля", null=True)
    car_model = models.CharField(verbose_name="Модель автомобиля", null=True)
    car_year = models.CharField(verbose_name="Год автомобиля", null=True)
    car_color = models.CharField(verbose_name="Цвет автомобиля", null=True)
    car_country = models.CharField(verbose_name="Страна, где авто на учете", null=True)
    car_number = models.CharField(verbose_name="Номер автомобиля", null=True)
    approved = models.BooleanField(verbose_name="подтверждено", default=False)
    image = models.ImageField(verbose_name="Фотография", upload_to="images/cars", null=True)


class Driver(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.PositiveIntegerField(verbose_name="Рейтинг", default=0)
    approved = models.BooleanField(verbose_name="Подтвержден", default=True)
