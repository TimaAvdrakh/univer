# Generated by Django 2.2.4 on 2020-06-09 10:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('applicant', '0048_auto_20200608_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicationstatuschangehistory',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    to='portal_users.Profile', unique=True, verbose_name='Заявитель'),
        ),
    ]
