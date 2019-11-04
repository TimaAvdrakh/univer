# Generated by Django 2.2.4 on 2019-11-04 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0056_auto_20191101_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='disciplinecycle',
            name='short_name',
            field=models.CharField(default='', max_length=10, verbose_name='Краткое название'),
        ),
        migrations.AlterField(
            model_name='disciplinecomponent',
            name='short_name',
            field=models.CharField(default='', max_length=10, verbose_name='Краткое название'),
        ),
        migrations.AlterField(
            model_name='disciplinecomponent',
            name='short_name_en',
            field=models.CharField(default='', max_length=10, null=True, verbose_name='Краткое название'),
        ),
        migrations.AlterField(
            model_name='disciplinecomponent',
            name='short_name_kk',
            field=models.CharField(default='', max_length=10, null=True, verbose_name='Краткое название'),
        ),
        migrations.AlterField(
            model_name='disciplinecomponent',
            name='short_name_ru',
            field=models.CharField(default='', max_length=10, null=True, verbose_name='Краткое название'),
        ),
    ]
