# Generated by Django 2.2.4 on 2019-12-03 06:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0033_auto_20191201_1205'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsernameRule',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('raw_username', models.CharField(max_length=500, verbose_name='Логин')),
                ('order', models.IntegerField(verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'Правило создания логина',
                'verbose_name_plural': 'Правила создания логина',
            },
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL),
        ),
    ]