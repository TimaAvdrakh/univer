# Generated by Django 2.2.4 on 2020-05-04 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0029_auto_20200429_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='docscan',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
