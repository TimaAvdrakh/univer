# Generated by Django 2.2.4 on 2020-01-27 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0051_auto_20200115_1436'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='is_selection_committer',
            field=models.BooleanField(default=False, verbose_name='Специалист приемной комиссии'),
        ),
    ]