# Generated by Django 2.2.4 on 2020-06-19 10:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0032_auto_20200611_1722'),
        ('applicant', '0055_auto_20200619_1146'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='document1c',
            unique_together={('campaign', 'type')},
        ),
    ]