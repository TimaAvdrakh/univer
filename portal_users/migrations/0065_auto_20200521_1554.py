# Generated by Django 2.2.4 on 2020-05-21 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0064_remove_role_is_selection_committer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='middle_name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Отчество'),
        ),
    ]
