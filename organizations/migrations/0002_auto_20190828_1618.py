# Generated by Django 2.2.4 on 2019-08-28 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='name_en',
            field=models.CharField(max_length=500, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='organization',
            name='name_kz',
            field=models.CharField(max_length=500, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='organization',
            name='name_ru',
            field=models.CharField(max_length=500, null=True, verbose_name='Название'),
        ),
    ]
