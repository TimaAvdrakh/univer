# Generated by Django 2.2.4 on 2020-04-29 09:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0063_auto_20200427_1240'),
        ('applicant', '0027_auto_20200428_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='portal_users.Profile'),
        ),
        migrations.AddField(
            model_name='privilege',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='portal_users.Profile'),
        ),
        migrations.AddField(
            model_name='userprivilegelist',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='portal_users.Profile'),
        ),
    ]