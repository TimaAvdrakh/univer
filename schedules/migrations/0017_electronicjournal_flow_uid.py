# Generated by Django 2.2.4 on 2019-11-27 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0016_auto_20191127_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='electronicjournal',
            name='flow_uid',
            field=models.UUIDField(null=True, verbose_name='UID потока'),
        ),
    ]