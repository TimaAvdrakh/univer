# Generated by Django 2.2.4 on 2020-05-19 05:55

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0027_auto_20200505_1909'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTypeGroup',
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
                'verbose_name': 'Группа типов документа',
                'verbose_name_plural': 'Группы типов документов',
            },
        ),
        migrations.AddField(
            model_name='documenttype',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.DocumentTypeGroup', verbose_name='Группа типов'),
        ),
    ]
