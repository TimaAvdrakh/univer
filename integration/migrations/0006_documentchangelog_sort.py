# Generated by Django 2.2.4 on 2020-01-28 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integration', '0005_documentchangelog_sent_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentchangelog',
            name='sort',
            field=models.IntegerField(default=500),
        ),
    ]
