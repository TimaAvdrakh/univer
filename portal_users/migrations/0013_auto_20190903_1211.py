# Generated by Django 2.2.4 on 2019-09-03 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0012_auto_20190902_1648'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='study_form',
        ),
        migrations.AddField(
            model_name='profile',
            name='course',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Курс'),
        ),
    ]