# Generated by Django 2.2.4 on 2020-03-18 10:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0055_auto_20200225_1056'),
        ('advisors', '0009_auto_20200318_0440'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='themesoftheses',
            unique_together={('uid_1c', 'student')},
        ),
    ]