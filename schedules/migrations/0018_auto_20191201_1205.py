# Generated by Django 2.2.4 on 2019-12-01 06:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0017_electronicjournal_flow_uid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='electronicjournal',
            name='stud_disciplines',
        ),
        migrations.RemoveField(
            model_name='electronicjournal',
            name='study_end',
        ),
        migrations.RemoveField(
            model_name='electronicjournal',
            name='study_start',
        ),
    ]