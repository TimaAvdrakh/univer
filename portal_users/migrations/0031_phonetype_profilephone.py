# Generated by Django 2.2.4 on 2019-11-29 09:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0030_auto_20191112_1132'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhoneType',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=200, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=200, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=200, null=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тип телефона',
                'verbose_name_plural': 'Типы телефона',
            },
        ),
        migrations.CreateModel(
            name='ProfilePhone',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('value', models.CharField(max_length=15, verbose_name='Номер телефона')),
                ('phone_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='portal_users.PhoneType', verbose_name='Тип телефона')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phones', to='portal_users.Profile', verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'Телефон Пользователя',
                'verbose_name_plural': 'Телефоны Пользователей',
            },
        ),
    ]
