# Generated by Django 2.2.4 on 2020-07-15 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0067_auto_20200630_1352'),
        ('applicant', '0061_auto_20200713_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='phone2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='portal_users.ProfilePhone', verbose_name='Телефон дополнительный'),
        ),
    ]
