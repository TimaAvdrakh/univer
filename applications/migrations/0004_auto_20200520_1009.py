# Generated by Django 2.2.4 on 2020-05-20 10:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0003_auto_20200430_0934'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subapplication',
            unique_together={('id',)},
        ),
    ]
