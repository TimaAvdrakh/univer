# Generated by Django 2.2.4 on 2020-01-28 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c1', '0002_auto_20191218_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='c1object',
            name='sort',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='c1objectcompare',
            name='sort',
            field=models.IntegerField(default=500),
        ),
    ]
