# Generated by Django 2.2.4 on 2020-07-30 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0070_profilephone_modified_for_1c'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='is_columnist',
            field=models.BooleanField(default=False, help_text='Ведет новостной блок портала', verbose_name='Колумнист'),
        ),
    ]