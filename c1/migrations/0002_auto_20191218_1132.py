# Generated by Django 2.2.4 on 2019-12-18 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c1', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='c1object',
            name='name',
            field=models.CharField(max_length=800, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='c1objectcompare',
            name='name',
            field=models.CharField(max_length=800, verbose_name='Название'),
        ),
    ]
