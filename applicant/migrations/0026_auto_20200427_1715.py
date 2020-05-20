# Generated by Django 2.2.4 on 2020-04-27 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0025_auto_20200426_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addressclassifier',
            name='code',
            field=models.PositiveIntegerField(unique=True, verbose_name='Код'),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='email',
            field=models.EmailField(max_length=100, unique=True, verbose_name='Email'),
        ),
    ]