# Generated by Django 2.2.4 on 2019-11-12 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0029_auto_20191008_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='is_supervisor',
            field=models.BooleanField(default=False, verbose_name='Эдвайзор'),
        ),
    ]
