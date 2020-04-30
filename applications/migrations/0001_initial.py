# Generated by Django 2.2.4 on 2020-04-27 10:32

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portal_users', '0056_merge_20200312_1209'),
    ]

    operations = [
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='media', verbose_name='Файл')),
                ('path', models.TextField(blank=True, null=True, verbose_name='Path to file')),
                ('ext', models.CharField(blank=True, max_length=20, null=True, verbose_name='File extension')),
                ('name', models.CharField(blank=True, max_length=500, null=True, verbose_name='File name')),
                ('size', models.PositiveIntegerField(blank=True, null=True, verbose_name='File size')),
                ('content_type', models.CharField(blank=True, max_length=500, null=True, verbose_name='Content type of a file')),
            ],
            options={
                'verbose_name': 'Example',
            },
        ),
        migrations.CreateModel(
            name='Status',
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
                ('code', models.CharField(blank=True, editable=False, max_length=100, null=True)),
                ('c1_id', models.CharField(blank=True, default='', max_length=100, verbose_name='Ид в 1с')),
            ],
            options={
                'verbose_name': 'Статус заявки',
                'verbose_name_plural': 'Статусы заявок',
            },
        ),
        migrations.CreateModel(
            name='Type',
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
                ('code', models.CharField(blank=True, editable=False, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Тип заявки',
                'verbose_name_plural': 'Типы заявок',
            },
        ),
        migrations.CreateModel(
            name='IdentityDoc',
            fields=[
                ('example_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='applications.Example')),
            ],
            options={
                'verbose_name': 'Identity document',
            },
            bases=('applications.example',),
        ),
        migrations.CreateModel(
            name='ServiceDoc',
            fields=[
                ('example_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='applications.Example')),
            ],
            options={
                'verbose_name': 'Service virtual document',
            },
            bases=('applications.example',),
        ),
        migrations.CreateModel(
            name='SubType',
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
                ('code', models.CharField(blank=True, editable=False, max_length=100, null=True)),
                ('example', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applications.Example', verbose_name='Document example')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='applications.Type', verbose_name='Type')),
            ],
            options={
                'verbose_name': 'Вид справки',
                'verbose_name_plural': 'Виды справок',
            },
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('send', models.BooleanField(default=False, verbose_name='Is send to 1C')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students_profile', to='portal_users.Profile', verbose_name='Профиль')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='applications.Type')),
                ('identity_doc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applications.IdentityDoc', verbose_name='Identity document')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
            },
        ),
        migrations.CreateModel(
            name='SubApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('organization', models.TextField(default='', null=True)),
                ('lang', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=20), default=list, size=3, verbose_name='Языки')),
                ('is_paper', models.BooleanField(default=True, verbose_name='Бумажный вариант')),
                ('copies', models.PositiveSmallIntegerField(blank=True, default=1, null=True, verbose_name='Copies')),
                ('responsible', models.CharField(blank=True, default='', max_length=200, verbose_name='Ответственный специалист')),
                ('comment', models.TextField(blank=True, default='', null=True, verbose_name='Комментарий к статусу')),
                ('application', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='applications.Application')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applications.Status', verbose_name='Status')),
                ('subtype', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='applications.SubType')),
                ('result_doc', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applications.ServiceDoc', verbose_name='Result document')),
            ],
            options={
                'verbose_name': 'Справка',
                'verbose_name_plural': 'Справки',
            },
        ),
    ]
