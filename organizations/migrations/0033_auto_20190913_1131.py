# Generated by Django 2.2.4 on 2019-09-13 05:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0032_educationprogram_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationbase',
            name='name_en',
            field=models.CharField(max_length=200, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='educationbase',
            name='name_kk',
            field=models.CharField(max_length=200, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='educationbase',
            name='name_ru',
            field=models.CharField(max_length=200, null=True, verbose_name='Название'),
        ),
        migrations.AddField(
            model_name='studyplan',
            name='education_base',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.EducationBase', verbose_name='Основа обучения'),
        ),
    ]