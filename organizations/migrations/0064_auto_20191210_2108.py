# Generated by Django 2.2.4 on 2019-12-10 15:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0063_auto_20191209_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacherdiscipline',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.Language', verbose_name='Язык преподавания'),
        ),
    ]
