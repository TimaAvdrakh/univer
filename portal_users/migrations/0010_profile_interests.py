# Generated by Django 2.2.4 on 2019-08-29 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0009_auto_20190829_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='interests',
            field=models.ManyToManyField(blank=True, related_name='profiles', to='portal_users.Interest', verbose_name='Увлечения'),
        ),
    ]