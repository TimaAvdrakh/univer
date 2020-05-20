# Generated by Django 2.2.4 on 2020-04-21 13:55

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('common', '0024_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Changelog',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('key', models.CharField(max_length=300, verbose_name='Ключ')),
                ('old_value', models.CharField(blank=True, default='', max_length=300, verbose_name='Старое значение')),
                ('new_value', models.CharField(blank=True, default='', max_length=300, verbose_name='Новое значение')),
                ('object_id', models.CharField(blank=True, editable=False, max_length=50, null=True)),
                ('content_type', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Изменения заявления',
                'verbose_name_plural': 'Изменения заявлений',
            },
        ),
    ]
