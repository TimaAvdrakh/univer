# Generated by Django 2.2.4 on 2020-06-08 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('applicant', '0047_merge_20200601_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationstatuschangehistory',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='portal_users.Profile', verbose_name='Заявитель'),
        ),
    ]
