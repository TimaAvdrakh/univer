# Generated by Django 2.2.4 on 2020-04-30 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0002_auto_20200430_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtype',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='type',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
    ]