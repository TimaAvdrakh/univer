# Generated by Django 2.2.4 on 2020-08-04 11:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0135_auto_20200803_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentdiscipline',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='language', to='organizations.Language', verbose_name='Язык'),
        ),
    ]
