# Generated by Django 2.2.4 on 2019-12-11 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0015_auto_20191211_1348'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='creditcoeff',
            unique_together={('start_year', 'coeff')},
        ),
    ]
