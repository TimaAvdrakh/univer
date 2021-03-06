# Generated by Django 2.2.4 on 2020-04-03 13:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0115_auto_20200403_1152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='education',
            name='avg_mark',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(3.7)], verbose_name='Средняя оценка (не выще 3.7)'),
        ),
        migrations.AlterField(
            model_name='education',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='educations', to='portal_users.Profile', verbose_name='Пользователь'),
        ),
    ]
