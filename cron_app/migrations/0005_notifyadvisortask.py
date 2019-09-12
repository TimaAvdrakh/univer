# Generated by Django 2.2.4 on 2019-09-12 04:13

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0031_auto_20190910_1552'),
        ('cron_app', '0004_credentialsemailtask'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotifyAdvisorTask',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('is_success', models.BooleanField(default=False, verbose_name='Успешно')),
                ('stud_discipline_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.StudentDisciplineInfo', verbose_name='Инфо о выборе студента')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
