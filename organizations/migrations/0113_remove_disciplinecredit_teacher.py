# Generated by Django 2.2.4 on 2020-03-13 11:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0112_auto_20200310_0951'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='disciplinecredit',
            name='teacher',
        ),
    ]
