# Generated by Django 2.2.4 on 2020-08-04 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0071_role_is_columnist'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='role',
            name='is_mod_can_edit',
        ),
    ]
