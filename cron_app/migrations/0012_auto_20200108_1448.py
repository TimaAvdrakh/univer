# Generated by Django 2.2.4 on 2020-01-08 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cron_app', '0011_exceltask'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exceltask',
            name='file',
        ),
        migrations.AddField(
            model_name='exceltask',
            name='file_path',
            field=models.CharField(default='', max_length=1000),
        ),
    ]
