# Generated by Django 2.2.4 on 2019-12-09 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0019_studentperformancelog'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='electronicjournal',
            name='status',
        ),
        migrations.AddField(
            model_name='electronicjournal',
            name='closed',
            field=models.BooleanField(default=False, verbose_name='Закрыт'),
        ),
    ]