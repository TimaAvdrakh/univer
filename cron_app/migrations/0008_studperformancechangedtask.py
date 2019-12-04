# Generated by Django 2.2.4 on 2019-12-04 06:53

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0018_auto_20191201_1205'),
        ('portal_users', '0034_auto_20191203_1243'),
        ('cron_app', '0007_advisorrejectedbidtask'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudPerformanceChangedTask',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('is_success', models.BooleanField(default=False, verbose_name='Успешно')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal_users.Profile', verbose_name='Автор')),
                ('new_mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedules.Mark', verbose_name='Новая оценка')),
                ('old_mark', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='schedules.Mark', verbose_name='Старая оценка')),
                ('stud_perf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedules.StudentPerformance', verbose_name='Успеваемость студента')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
