# Generated by Django 2.2.4 on 2019-09-04 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0014_auto_20190904_1419'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievement',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='achievements', to='portal_users.Profile', verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='role',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='portal_users.Profile', verbose_name='Пользователь'),
        ),
    ]
