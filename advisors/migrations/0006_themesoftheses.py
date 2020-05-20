# Generated by Django 2.2.4 on 2020-03-12 10:35

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0112_auto_20200310_0951'),
        ('portal_users', '0055_auto_20200225_1056'),
        ('advisors', '0005_auto_20191031_0954'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThemesOfTheses',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('supervisor_leader', models.CharField(blank=True, max_length=1000, null=True, verbose_name='Руководитель извне')),
                ('acad_period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.AcadPeriod', verbose_name='Академический период')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_themes_theses', to='portal_users.Profile', verbose_name='Обучающийся')),
                ('study_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.StudyPlan', verbose_name='Учебный план')),
                ('supervisors', models.ManyToManyField(related_name='supervisors_themes_theses', to='portal_users.Profile', verbose_name='Руководители')),
            ],
            options={
                'verbose_name': 'Тема дипломной работы',
                'verbose_name_plural': 'Темы дипломных работ',
            },
        ),
    ]