# Generated by Django 2.2.4 on 2019-12-19 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0028_lesson_closed'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='admin_allow',
            field=models.BooleanField(default=False, verbose_name='Разрешение админа'),
        ),
    ]