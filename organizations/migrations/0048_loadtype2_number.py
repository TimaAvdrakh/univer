# Generated by Django 2.2.4 on 2019-10-08 05:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0047_auto_20191008_0924'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadtype2',
            name='number',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Номер'),
        ),
    ]