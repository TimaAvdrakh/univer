# Generated by Django 2.2.4 on 2020-06-30 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0032_auto_20200611_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='citizenship',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='document',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='documenttype',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='documenttypegroup',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='governmentagency',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='nationality',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='registrationperiod',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
