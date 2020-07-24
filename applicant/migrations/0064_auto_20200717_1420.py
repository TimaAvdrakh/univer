# Generated by Django 2.2.4 on 2020-07-17 08:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0063_auto_20200716_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='phone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phones', to='portal_users.ProfilePhone', verbose_name='Телефон'),
        ),
    ]