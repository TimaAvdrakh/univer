# Generated by Django 2.2.4 on 2019-12-25 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integration', '0003_documentchangelog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentchangelog',
            name='errors',
            field=models.TextField(blank=True, default='', verbose_name='Ошибки'),
        ),
    ]
