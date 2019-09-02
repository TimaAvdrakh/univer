# Generated by Django 2.2.4 on 2019-08-28 11:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0004_auto_20190828_1759'),
        ('cron_app', '0002_auto_20190828_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResetPasswordUrlSendTask',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('is_success', models.BooleanField(default=False, verbose_name='Успешно')),
                ('reset_password', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal_users.ResetPassword')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]