# Generated by Django 2.2.4 on 2019-11-12 05:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0058_auto_20191104_1114'),
        ('common', '0011_creditcoeff'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrationperiod',
            name='study_year',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.StudyPeriod', verbose_name='Учебный год'),
        ),
    ]
