# Generated by Django 2.2.4 on 2020-02-05 05:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0053_auto_20200128_1317'),
        ('organizations', '0105_auto_20200204_1537'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='studentdiscipline',
            unique_together={('student', 'study_plan_uid_1c', 'acad_period', 'discipline_code', 'discipline', 'load_type', 'hours', 'cycle', 'study_year')},
        ),
    ]
