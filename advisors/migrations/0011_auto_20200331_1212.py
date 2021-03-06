# Generated by Django 2.2.4 on 2020-03-31 06:12

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('advisors', '0010_auto_20200318_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='themesoftheses',
            name='sent',
            field=models.NullBooleanField(default=False, verbose_name='Отправлен в 1С'),
        ),
        migrations.AlterField(
            model_name='themesoftheses',
            name='uid_1c',
            field=models.CharField(blank=True, default='', help_text='придет, после выгрузки в 1С', max_length=100,
                                   null=True, verbose_name='УИД документа-аналога в 1С'),
        ),
    ]
