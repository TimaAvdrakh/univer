# Generated by Django 2.2.4 on 2019-12-24 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0076_studentdiscipline_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdiscipline',
            name='uid_1c',
            field=models.CharField(blank=True, default='', help_text='придет, после выгрузки в 1С', max_length=100, verbose_name='УИД документа-аналога в 1С'),
        ),
    ]
