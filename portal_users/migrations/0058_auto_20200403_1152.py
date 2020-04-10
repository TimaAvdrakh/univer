# Generated by Django 2.2.4 on 2020-04-03 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0057_role_is_mod'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievementtype',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='gender',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='interest',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='level',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='maritalstatus',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='phonetype',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='position',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='studentstatus',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
    ]
