# Generated by Django 2.2.4 on 2019-12-09 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0061_loadtype2_uid_1c'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadtype',
            name='parent_uid_1c',
            field=models.CharField(default='', max_length=200, verbose_name='УИД 1С родителя'),
        ),
    ]