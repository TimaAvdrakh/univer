# Generated by Django 2.2.4 on 2019-12-11 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0067_auto_20191211_1431'),
        ('portal_users', '0043_auto_20191211_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacherposition',
            name='study_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.StudyPeriod', verbose_name='Учебный год'),
        ),
    ]