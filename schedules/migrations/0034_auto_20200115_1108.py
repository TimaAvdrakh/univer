# Generated by Django 2.2.4 on 2020-01-15 05:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0033_electronicjournal_plan_block_date'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together=set(),
        ),
    ]
