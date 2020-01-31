# Generated by Django 2.2.4 on 2020-01-28 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0034_auto_20200115_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='electronicjournal',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='gradingsystem',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='lesson',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='lessonstatus',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='lessonstudent',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='lessonteacher',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='mark',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='room',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='roomtype',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='studentperformance',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='studentperformancelog',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='timewindow',
            name='sort',
            field=models.IntegerField(default=500),
        ),
    ]