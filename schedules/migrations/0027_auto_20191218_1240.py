# Generated by Django 2.2.4 on 2019-12-18 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0026_auto_20191218_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentperformance',
            name='missed',
            field=models.BooleanField(default=True, verbose_name='Отсутствовал'),
        ),
    ]
