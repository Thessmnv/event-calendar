from django.db import models
from django.contrib.auth.models import User


class Venue(models.Model):
    name = models.CharField('Название места проведения', max_length=120)
    address = models.CharField('Адрес', max_length=300)
    phone = models.CharField('Контактный номер', max_length=25, blank=True)
    web = models.URLField('Веб-сайт', blank=True)
    owner = models.IntegerField('Владелец места', blank=False, default=1)
    venue_image = models.ImageField(null=True, blank=True, upload_to='images/')

    def __str__(self):
        return self.name


class CalendarUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField('Электронная почта пользователя')

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Event(models.Model):
    name = models.CharField('Название', max_length=150)
    event_date = models.DateTimeField('Дата и время')
    venue = models.ForeignKey(Venue, blank=True, null=True, on_delete=models.CASCADE, verbose_name='Место')
    # venue = models.CharField(max_length=120)
    manager = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Организатор')
    description = models.TextField('Описание', blank=True)
    attendees = models.ManyToManyField(CalendarUser, blank=True, verbose_name='Участники')
    approved = models.BooleanField('Подтвердить', default=False)

    def __str__(self):
        return self.name
