# Generated by Django 2.2.4 on 2019-10-09 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0048_loadtype2_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdiscipline',
            name='study_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.StudyPeriod', verbose_name='Учебный год'),
        ),
    ]
