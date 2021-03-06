# Generated by Django 2.2.4 on 2019-12-18 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0047_auto_20191218_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='birth_place',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='Место рождения'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='first_name',
            field=models.CharField(max_length=200, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='first_name_en',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Имя на английском'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='iin',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='ИИН'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_name',
            field=models.CharField(max_length=200, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='last_name_en',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Фамилия на английском'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='middle_name',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Телефон'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='skype',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Skype'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='academic_degree',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Ученая степень'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='academic_rank',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Ученое звание'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='work_experience_year',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Стаж работы в ВУЗ (Год)'),
        ),
    ]
