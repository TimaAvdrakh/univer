# Generated by Django 2.2.4 on 2020-04-06 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0011_auto_20200403_1909'),
    ]

    operations = [
        migrations.AddField(
            model_name='admissioncampaigntype',
            name='name_en',
            field=models.CharField(max_length=800, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='admissioncampaigntype',
            name='name_kk',
            field=models.CharField(max_length=800, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='admissioncampaigntype',
            name='name_ru',
            field=models.CharField(max_length=800, null=True, verbose_name='Название'),
        ),
    ]
