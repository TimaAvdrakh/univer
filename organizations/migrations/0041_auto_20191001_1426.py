# Generated by Django 2.2.4 on 2019-10-01 08:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0040_auto_20191001_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studyyearcourse',
            name='study_plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='study_year_courses', to='organizations.StudyPlan', verbose_name='Учебный план'),
        ),
    ]