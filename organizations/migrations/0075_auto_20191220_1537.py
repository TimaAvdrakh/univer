# Generated by Django 2.2.4 on 2019-12-20 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0049_profile_password_changed'),
        ('organizations', '0074_auto_20191220_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='studyplan',
            name='uid_1c',
            field=models.CharField(max_length=100, null=True, verbose_name='uid 1C'),
        ),
        migrations.AlterField(
            model_name='studentdiscipline',
            name='study_plan_uid_1c',
            field=models.CharField(max_length=100, null=True, verbose_name='uid 1c учебного плана'),
        ),
        migrations.AlterUniqueTogether(
            name='studentdiscipline',
            unique_together={('student', 'study_plan_uid_1c', 'acad_period', 'discipline_code', 'discipline', 'load_type', 'hours', 'language', 'cycle', 'study_year')},
        ),
        migrations.AlterUniqueTogether(
            name='studyplan',
            unique_together={('student', 'uid_1c')},
        ),
    ]