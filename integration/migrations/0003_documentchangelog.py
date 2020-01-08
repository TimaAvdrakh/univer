# Generated by Django 2.2.4 on 2019-12-24 10:25

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('integration', '0002_delete_studentdisciplinelog'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentChangeLog',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('object_id', models.UUIDField(null=True)),
                ('status', models.IntegerField(choices=[(0, 'Данные были успешно загружены'), (1, 'Данные не были загружены'), (2, 'Данные были загружены с ошибками')], verbose_name='Статус обмена')),
                ('errors', models.CharField(blank=True, default='', max_length=1000, verbose_name='Ошибки')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name': 'Лог обмена документами',
                'verbose_name_plural': 'Логи обмена документами',
            },
        ),
    ]