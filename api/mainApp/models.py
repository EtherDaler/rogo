import datetime

from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

from auth.models import User


def default_datetime(): 
    return datetime.datetime.now()


class Rides(models.Model):
    author = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = 'Создатель поездки', blank = True, null = True)
    date_create = models.DateTimeField(default=default_datetime(), null=True, blank = True, verbose_name = 'Дата создания')
    pick_up_location = models.CharField(max_length=120, verbose_name='Место сбора')
    drop_location = models.CharField(max_length=120, verbose_name='Пункт назначения')
    total_rides = models.IntegerField(verbose_name='Количество пассажиров(мин=1, макс=10)', validators=[MaxValueValidator(10),MinValueValidator(1)])
    #luggage = models.BooleanField(verbose_name='Возможность принять посылку/груз', default=False)
    true = models.BooleanField(default=True)
    false = models.BooleanField(default=False)
    date = models.DateField(verbose_name='Дата(гг-мм-дд)')
    time= models.TimeField(verbose_name='Время(ч:м)',auto_now=False, auto_now_add=False, null=True)
    price = models.CharField(max_length=120,verbose_name='Цена (с.)', default='')
    #luggage_price = models.CharField(max_length=120, verbose_name='Цена за кг груза (с.)', blank = True, null = True)
    car = models.CharField(max_length=120,default='',verbose_name='Марка авто')
    car_number = models.CharField(max_length=12, verbose_name = 'Номер машины (01 0000 GG)', default = '')
    car_year_issue = models.CharField(max_length=4, verbose_name='Год выпуска машины', default = '')
    phone_number = models.CharField(max_length=15, default='', verbose_name='Номер телефона (используйте в начале код страны)')
    def __str__(self):
        return '%s - %s : %s' % (self.pick_up_location,self.drop_location,self.date) # отображение в качестве названия объекта БД


    class Meta:
        verbose_name='Поездку' # отображение нужного названия в админ панели при редактировании
        verbose_name_plural='Поездки' # отображенпие нужного названия в панели админа


class Join (models.Model):
    ride = models.ForeignKey(Rides, on_delete = models.CASCADE, verbose_name = 'Пользователь', blank = True, null = True, related_name = 'join_rides')
    author = models.ForeignKey(User, on_delete = models.CASCADE, verbose_name = 'Пользователь', blank = True, null = True)
    author_phone = models.CharField(max_length=13, default='', verbose_name='Номер телефона (используйте в начале код страны со знаком +)')
    status = models.BooleanField(verbose_name='видимость',default=False)
    
    def __str__(self):
        return '%s присоединен к поездке: %s - %s' % (self.author, self.ride.pick_up_location, self.ride.drop_location) # отображение в качестве названия объекта БД

    class Meta:
        verbose_name='Попутчиков' # отображение нужного названия в админ панели при редактировании
        verbose_name_plural='Попутчики' # отображенпие нужного названия в панели админа
