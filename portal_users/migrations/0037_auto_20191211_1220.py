# Generated by Django 2.2.4 on 2019-12-11 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0036_auto_20191211_1218'),
    ]

    operations = [
        migrations.RenameField(
            model_name='role',
            old_name='profile',
            new_name='profile_old',
        ),
    ]
