# Generated by Django 2.2.4 on 2020-01-10 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0081_teacherdiscipline_uid_1c'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdiscipline',
            name='uuid1c',
            field=models.CharField(default='', max_length=100, verbose_name='Уид 1С'),
        ),
    ]