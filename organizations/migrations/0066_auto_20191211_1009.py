# Generated by Django 2.2.4 on 2019-12-11 04:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0034_auto_20191203_1243'),
        ('organizations', '0065_teacherdiscipline_load_type2_uid_1c'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='teacherdiscipline',
            unique_together={('teacher', 'study_period', 'discipline', 'load_type2_uid_1c', 'language')},
        ),
    ]
