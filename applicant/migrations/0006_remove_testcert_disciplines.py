# Generated by Django 2.2.4 on 2020-03-26 03:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0005_application_creator'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testcert',
            name='disciplines',
        ),
    ]
