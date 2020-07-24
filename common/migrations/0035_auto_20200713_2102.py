# Generated by Django 2.2.4 on 2020-07-13 15:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0034_institutionconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='field_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Имя поля'),
        ),
        migrations.AddField(
            model_name='file',
            name='gen_uid',
            field=models.CharField(blank=True, max_length=36, null=True, verbose_name='сгенерированный UID'),
        ),
        migrations.AddField(
            model_name='file',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='files', to=settings.AUTH_USER_MODEL, verbose_name='Кто выгрузил'),
        ),
        migrations.CreateModel(
            name='ReservedUID',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Резервированный UID',
                'verbose_name_plural': "Резервированные UID'ы",
            },
        ),
    ]