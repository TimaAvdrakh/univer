# Generated by Django 2.2.4 on 2020-03-27 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('portal_users', '0056_merge_20200312_1209'),
        ('organizations', '0114_merge_20200327_1521'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='disciplinecredit',
        #     name='teacher',
        #     field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discipline_credit_teacher', to='portal_users.Profile', verbose_name='Преподаватель'),
        # ),
    ]