# Generated by Django 2.2.4 on 2020-07-14 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0035_auto_20200713_2102'),
        ('organizations', '0129_auto_20200630_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='files',
            field=models.ManyToManyField(blank=True, to='common.File', verbose_name='Сканы'),
        ),
    ]
