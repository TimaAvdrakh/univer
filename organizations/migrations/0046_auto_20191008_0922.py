# Generated by Django 2.2.4 on 2019-10-08 03:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0045_studyperiod_is_study_year'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='studyplan',
            unique_together=set(),
        ),
    ]
