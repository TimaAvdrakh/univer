# Generated by Django 2.2.4 on 2020-05-05 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0026_auto_20200505_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='identitydocument',
            name='serial_number',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Серия'),
        ),
    ]
