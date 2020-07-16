# Generated by Django 2.2.4 on 2020-07-13 01:28

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0129_auto_20200630_1352'),
        ('portal_users', '0067_auto_20200630_1352'),
        ('calendar_api', '0003_auto_20200709_1228'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='events',
            name='participants',
        ),
        migrations.CreateModel(
            name='Participants',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('cathedra', models.ManyToManyField(blank=True, related_name='events_cathedra', to='organizations.Cathedra', verbose_name='Кафедра')),
                ('education_program_groups', models.ManyToManyField(blank=True, related_name='events_education_program_groups', to='organizations.EducationProgramGroup', verbose_name='Группа образовательных программ')),
                ('education_programs', models.ManyToManyField(blank=True, related_name='events_education_program', to='organizations.EducationProgram', verbose_name='Образовательная программа')),
                ('faculty', models.ManyToManyField(blank=True, related_name='events_faculty', to='organizations.Faculty', verbose_name='Факультет')),
                ('group', models.ManyToManyField(blank=True, related_name='event_groups', to='organizations.Group', verbose_name='Учебная группа')),
                ('participant_profiles', models.ManyToManyField(blank=True, related_name='event_participant_profiles', to='portal_users.Profile', verbose_name='Профили участников события')),
                ('roles', models.ManyToManyField(blank=True, related_name='events_roles', to='portal_users.Role', verbose_name='Роли')),
            ],
            options={
                'verbose_name': 'Участник события',
                'verbose_name_plural': 'Участники события',
            },
        ),
        migrations.AddField(
            model_name='events',
            name='participants',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='calendar_api.Participants', verbose_name='Участники события'),
        ),
    ]
