# Generated by Django 2.2.4 on 2019-10-24 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0051_auto_20191022_0957'),
    ]

    operations = [
        migrations.AddField(
            model_name='discipline',
            name='code',
            field=models.CharField(default='', max_length=100, verbose_name='Код'),
        ),
    ]
