# Generated by Django 2.2.4 on 2020-04-20 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0020_auto_20200420_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='first_name_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя на латинице'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='last_name_en',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия на латинице'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='marital_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='portal_users.MaritalStatus', verbose_name='Семейное положение'),
        ),
    ]