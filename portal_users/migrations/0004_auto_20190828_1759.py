# Generated by Django 2.2.4 on 2019-08-28 11:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_studyform'),
        ('portal_users', '0003_auto_20190828_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gender',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_kz', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Пол',
                'verbose_name_plural': 'Полы',
            },
        ),
        migrations.CreateModel(
            name='MaritalStatus',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_kz', models.CharField(max_length=100, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=100, null=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Семейное положение',
                'verbose_name_plural': 'Семейное положение',
            },
        ),
        migrations.AddField(
            model_name='profile',
            name='study_form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='organizations.StudyForm', verbose_name='Форма обучения'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='skype',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Skype'),
        ),
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='portal_users.Gender', verbose_name='Пол'),
        ),
        migrations.AddField(
            model_name='profile',
            name='marital_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='portal_users.MaritalStatus', verbose_name='Семейное положение'),
        ),
    ]