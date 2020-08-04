# Generated by Django 2.2.4 on 2020-08-04 17:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0138_auto_20200804_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentdiscipline',
            name='discipline',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_discipline', to='organizations.Discipline', verbose_name='Дисциплина'),
        ),
        migrations.AlterField(
            model_name='studentdiscipline',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_language', to='organizations.Language', verbose_name='Язык'),
        ),
        migrations.AlterField(
            model_name='teacherdiscipline',
            name='discipline',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_discipline', to='organizations.Discipline', verbose_name='Дисциплина'),
        ),
        migrations.AlterField(
            model_name='teacherdiscipline',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teacher_language', to='organizations.Language', verbose_name='Язык преподавания'),
        ),
    ]
