from django.db import models
from common.models import BaseModel
from django.contrib.auth.models import User


class Profile(BaseModel):
    user = models.OneToOneField(
        User,
        related_name='profile',
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
    )
    middle_name = models.CharField(
        max_length=100,
        default='',
        verbose_name='Отчество',
        blank=True,
    )
    phone = models.CharField(
        max_length=20,
        default="",
        verbose_name='Телефон',
        blank=True,
    )
    avatar = models.ImageField(
        upload_to='users/',
        verbose_name='Аватар',
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
