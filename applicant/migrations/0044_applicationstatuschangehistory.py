# Generated by Django 2.2.4 on 2020-05-28 08:01

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ('portal_users', '0065_auto_20200521_1554'),
        ('common', '0031_auto_20200521_1750'),
        ('applicant', '0043_auto_20200525_1345'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationStatusChangeHistory',
            fields=[
                ('uid',
                 models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True,
                                  verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                              to='common.Comment', verbose_name='Комментарий изменения')),
                ('creator', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                                 to='portal_users.Profile', verbose_name='Заявитель')),
                ('status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                             to='applicant.ApplicationStatus', verbose_name='Статус')),
            ],
            options={
                'verbose_name': 'История изменения статуса заявления',
                'verbose_name_plural': 'История изменения статуса заявлений',
            },
        ),
    ]