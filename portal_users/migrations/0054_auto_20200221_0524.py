# Generated by Django 2.2.4 on 2020-02-21 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0053_auto_20200128_1317'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='interest',
            index=models.Index(fields=['profile'], name='portal_user_profile_2416d1_idx'),
        ),
    ]