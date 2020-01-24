# Generated by Django 2.2.4 on 2020-01-20 11:04

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0085_controlform'),
    ]

    operations = [
        # migrations.CreateModel(
        #     name='DisciplineCredit',
        #     fields=[
        #         ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
        #         ('is_active', models.BooleanField(default=True)),
        #         ('created', models.DateTimeField(auto_now_add=True)),
        #         ('updated', models.DateTimeField(auto_now=True)),
        #         ('deleted', models.DateTimeField(blank=True, null=True)),
        #         ('uuid1c', models.CharField(editable=False, max_length=100, verbose_name='Уид 1С')),
        #         ('credit', models.FloatField(verbose_name='Кредит')),
        #         ('control_form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.ControlForm', verbose_name='Форма контроля')),
        #         ('cycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.DisciplineCycle', verbose_name='Цикл дисциплины')),
        #         ('discipline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.Discipline', verbose_name='Дисциплина')),
        #         ('study_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.StudyPlan', verbose_name='Учебный план')),
        #     ],
        #     options={
        #         'verbose_name': 'Кредит дисциплины',
        #         'verbose_name_plural': 'Кредиты дисциплин',
        #     },
        # ),
    ]
