# Generated by Django 2.2.4 on 2019-09-04 08:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0011_auto_20190904_1408'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='education',
            name='user',
        ),
        migrations.RemoveField(
            model_name='teacherdiscipline',
            name='teacher',
        ),
    ]
