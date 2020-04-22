# Generated by Django 2.2.4 on 2020-04-22 04:26

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0059_merge_20200410_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfoShowPermission',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('first_name_en', models.BooleanField(default=True, verbose_name='Имя')),
                ('last_name_en', models.BooleanField(default=True, verbose_name='Фамилия')),
                ('birth_date', models.BooleanField(default=True, verbose_name='Дата рождения')),
                ('birth_place', models.BooleanField(default=True, verbose_name='Место рождения')),
                ('nationality', models.BooleanField(default=True, verbose_name='Национальность')),
                ('citizenship', models.BooleanField(default=True, verbose_name='Гражданство')),
                ('gender', models.BooleanField(default=True, verbose_name='Пол')),
                ('marital_status', models.BooleanField(default=True, verbose_name='Семейное положение')),
                ('address', models.BooleanField(default=True, verbose_name='Адрес')),
                ('phone', models.BooleanField(default=True, verbose_name='Телефон')),
                ('email', models.BooleanField(default=True, verbose_name='Email')),
                ('skype', models.BooleanField(default=True, verbose_name='Skype')),
                ('interests', models.BooleanField(default=True, verbose_name='Интересы')),
                ('extra_data', models.BooleanField(default=True, verbose_name='Дополнительная информация')),
                ('iin', models.BooleanField(default=True, verbose_name='ИИН')),
                ('identity_documents', models.BooleanField(default=True, verbose_name='Документ')),
                ('education', models.BooleanField(default=True, verbose_name='Информация об образовании')),
                ('profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='info_show_permission', to='portal_users.Profile', verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'Разрешения для отображения инфо пользователя',
            },
        ),
    ]
