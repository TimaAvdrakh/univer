# Generated by Django 2.2.4 on 2020-07-23 11:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0036_identitydocument_uid_1c'),
    ]

    operations = [
        migrations.AddField(
            model_name='institutionconfig',
            name='max_file_size',
            field=models.PositiveIntegerField(blank=True, default=10, null=True, validators=[django.core.validators.MaxValueValidator(500)], verbose_name='Максимально допустимый размер файла (в мегабайтах МБ)'),
        ),
    ]