# Generated by Django 2.2.4 on 2019-12-11 06:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0041_auto_20191211_1227'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='profilephone',
            unique_together={('profile', 'phone_type', 'value')},
        ),
    ]
