# Generated by Django 2.2.4 on 2020-06-19 05:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0054_auto_20200617_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recruitmentplan',
            name='graduating_cathedra',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='organizations.Cathedra', verbose_name='Выпускающая кафедра'),
        ),
    ]
