from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from auth.models import Driver


class Rides(models.Model):
    driver = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        verbose_name='Создатель поездки',
        related_name='rides',
        blank=True,
        null=True,
    )
    date_create = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name='Дата создания')
    start_at = models.DateTimeField(verbose_name='Дата и время поездки', null=False, blank=False)
    pick_up_location = models.CharField(max_length=120, verbose_name='Место сбора')
    pick_up_location_latitude = models.FloatField(verbose_name='Широта места сбора', blank=True, null=True)
    pick_up_location_longitude = models.FloatField(verbose_name='Долгота места сбора', blank=True, null=True)
    drop_location = models.CharField(max_length=120, verbose_name='Пункт назначения')
    drop_location_latitude = models.FloatField(verbose_name='Широта пункта назначения', blank=True, null=True)
    drop_location_longitude = models.FloatField(verbose_name='Долгота пункта назначения', blank=True, null=True)
    total_rides = models.PositiveIntegerField(
        verbose_name='Количество пассажиров(мин=1, макс=10)',
        validators=[MaxValueValidator(10), MinValueValidator(1)],
    )
    luggage = models.BooleanField(verbose_name='Возможность принять посылку/груз', default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена (с.)')
    luggage_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за кг груза (с.)',
        blank=True,
        null=True,
    )
    
    def __str__(self):
        return '%s - %s : %s' % (self.pick_up_location, self.drop_location, self.start_at)


    class Meta:
        verbose_name='Поездку' # отображение нужного названия в админ панели при редактировании
        verbose_name_plural='Поездки' # отображенпие нужного названия в панели админа
        ordering = ["-start_at"]
        constraints = [
            models.CheckConstraint(check=models.Q(total_rides__gte=1), name="rides_total_rides_gte_1"),
        ]


class Join (models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "В ожидании"
        APPROVED = "approved", "Подтвержден"
        DECLINED = "declined", "Отклонен"

    ride = models.ForeignKey(
        Rides,
        on_delete=models.CASCADE,
        verbose_name='Поездка',
        blank=False,
        null=False,
        related_name='join_rides',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        blank=False,
        null=False,
        related_name='joined_rides',
    )
    status = models.CharField(verbose_name='Статус', choices=Status.choices, max_length=16, default=Status.PENDING)
    
    def __str__(self):
        return '%s присоединен к поездке: %s - %s' % (self.user, self.ride.pick_up_location, self.ride.drop_location)

    class Meta:
        verbose_name='Попутчиков' # отображение нужного названия в админ панели при редактировании
        verbose_name_plural='Попутчики' # отображенпие нужного названия в панели админа
        constraints = [
            models.UniqueConstraint(fields=["ride", "user"], name="unique_user_per_ride"),
        ]
