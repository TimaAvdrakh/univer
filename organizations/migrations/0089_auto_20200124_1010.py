# Generated by Django 2.2.4 on 2020-01-24 04:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0051_auto_20200115_1436'),
        ('organizations', '0088_auto_20200122_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentdiscipline',
            name='uuid1c',
            field=models.CharField(editable=False, max_length=100, null=True, verbose_name='Уид 1С'),
        ),
        # migrations.AlterUniqueTogether(
        #     name='studentdiscipline',
        #     unique_together={('student', 'study_plan_uid_1c', 'acad_period', 'discipline_code', 'discipline', 'load_type', 'hours', 'cycle', 'study_year')},
        # ),
    ]
