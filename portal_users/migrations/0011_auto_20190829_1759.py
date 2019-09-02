# Generated by Django 2.2.4 on 2019-08-29 11:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('portal_users', '0010_profile_interests'),
    ]

    operations = [
        migrations.CreateModel(
            name='AchievementType',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=500, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Тип достижения',
                'verbose_name_plural': 'Типы достижения',
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=500, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Уровень',
                'verbose_name_plural': 'Уровень',
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='extra_data',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='Дополнительная информация'),
        ),
        migrations.CreateModel(
            name='Achievement',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('content', models.CharField(max_length=1000, verbose_name='Тело')),
                ('achievement_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='portal_users.AchievementType', verbose_name='Тип достижения')),
                ('level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='portal_users.Level', verbose_name='Уровень')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Достижение',
                'verbose_name_plural': 'Достижения',
            },
        ),
    ]