# Generated by Django 2.2.4 on 2020-03-26 05:09

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cron_app', '0014_auto_20200128_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='exceltask',
            name='ordering',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=12), blank=True, default=None, null=True, size=12),
        ),
    ]
