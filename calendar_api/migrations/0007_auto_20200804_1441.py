# Generated by Django 2.2.4 on 2020-08-04 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendar_api', '0006_events_files'),
    ]

    operations = [
        migrations.AddField(
            model_name='repetitiontypes',
            name='name_en',
            field=models.CharField(max_length=800, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='repetitiontypes',
            name='name_kk',
            field=models.CharField(max_length=800, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='repetitiontypes',
            name='name_ru',
            field=models.CharField(max_length=800, null=True, verbose_name='Название'),
        ),
    ]
