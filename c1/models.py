# -*- coding: utf8 -*-
from __future__ import unicode_literals
from django.db import models

from common.models import BaseCatalog


class C1Object(BaseCatalog):
    model = models.CharField(
        verbose_name='Модель django',
        default='',
        max_length=100,
    )
    is_related = models.BooleanField(
        default=False,
        verbose_name='Это связанная модель',
    )

    class Meta:
        verbose_name = 'Объект интеграции с 1с'
        verbose_name_plural = 'Объекты интеграции с 1с'


class C1ObjectCompare(BaseCatalog):
    class Meta:
        verbose_name = 'Поле'
        verbose_name_plural = 'Поля'

    c1_object = models.ForeignKey(
        C1Object,
        on_delete=models.CASCADE,
        verbose_name='Объект интеграции',
    )
    c1 = models.CharField(
        verbose_name='Поле 1С',
        default='',
        max_length=100,
    )
    django = models.CharField(
        verbose_name='Поле Django',
        default='',
        max_length=100,
    )
    main_field = models.BooleanField(
        default=False,
        verbose_name='Ведущее поле',
    )
    is_binary_data = models.BooleanField(
        default=False,
        verbose_name='Двоичные данные',
    )
