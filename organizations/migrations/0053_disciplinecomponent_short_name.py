# Generated by Django 2.2.4 on 2019-10-30 03:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0052_discipline_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='disciplinecomponent',
            name='short_name',
            field=models.CharField(default='', max_length=10),
        ),
    ]
