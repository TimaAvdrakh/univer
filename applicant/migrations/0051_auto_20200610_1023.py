# Generated by Django 2.2.4 on 2020-06-10 04:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('applicant', '0050_auto_20200609_1601'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicationstatuschangehistory',
            old_name='creator',
            new_name='author',
        ),
    ]
