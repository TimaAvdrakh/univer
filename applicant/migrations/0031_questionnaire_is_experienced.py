# Generated by Django 2.2.4 on 2020-05-04 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0030_docscan_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='is_experienced',
            field=models.BooleanField(default=False),
        ),
    ]
