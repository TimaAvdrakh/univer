# Generated by Django 2.2.4 on 2020-04-28 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0007_subapplication_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'verbose_name': 'Статус', 'verbose_name_plural': 'Статусы'},
        ),
        migrations.AddField(
            model_name='status',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Code of status'),
        ),
    ]
