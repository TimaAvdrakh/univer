# Generated by Django 2.2.4 on 2019-12-11 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0040_auto_20191211_1224'),
    ]

    operations = [
        migrations.RenameField(
            model_name='role',
            old_name='profile_new',
            new_name='profile',
        ),
        migrations.RemoveField(
            model_name='role',
            name='profile_old',
        ),
    ]
