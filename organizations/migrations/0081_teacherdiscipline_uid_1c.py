# Generated by Django 2.2.4 on 2020-01-10 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0080_auto_20200104_1405'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherdiscipline',
            name='uid_1c',
            field=models.CharField(default='', max_length=100, verbose_name='Уид 1С'),
        ),
    ]