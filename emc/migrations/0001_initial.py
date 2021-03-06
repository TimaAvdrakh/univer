# Generated by Django 2.2.4 on 2020-07-21 09:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0130_education_files'),
        ('common', '0035_auto_20200713_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='EMC',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('description', models.TextField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('discipline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.Discipline')),
                ('files', models.ManyToManyField(to='common.File')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.Language')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
