# Generated by Django 2.2.4 on 2020-05-07 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0034_auto_20200506_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='is_grant_holder',
            field=models.BooleanField(default=False, verbose_name='Обладатель гранта'),
        ),
    ]