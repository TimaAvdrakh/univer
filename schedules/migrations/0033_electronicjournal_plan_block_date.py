# Generated by Django 2.2.4 on 2019-12-30 03:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0032_electronicjournal_block_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='electronicjournal',
            name='plan_block_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата запланированной блокировки'),
        ),
    ]