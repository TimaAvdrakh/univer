# Generated by Django 2.2.4 on 2019-12-11 11:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0021_delete_journalstatus'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('flow_uid', 'date', 'time')},
        ),
    ]
