# Generated by Django 2.2.4 on 2019-08-28 08:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0001_initial'),
        ('portal_users', '0002_resetpassword'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='id',
        ),
        migrations.RemoveField(
            model_name='resetpassword',
            name='id',
        ),
        migrations.AddField(
            model_name='profile',
            name='address',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='profile',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата рождения'),
        ),
        migrations.AddField(
            model_name='profile',
            name='birth_place',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Место рождения'),
        ),
        migrations.AddField(
            model_name='profile',
            name='citizenship',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Гражданство'),
        ),
        migrations.AddField(
            model_name='profile',
            name='document',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='Документ, удостоверяющий личность'),
        ),
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='profile',
            name='entry_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата поступления в ВУЗ'),
        ),
        migrations.AddField(
            model_name='profile',
            name='first_name_en',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Имя на английском'),
        ),
        migrations.AddField(
            model_name='profile',
            name='iin',
            field=models.IntegerField(blank=True, null=True, verbose_name='ИИН'),
        ),
        migrations.AddField(
            model_name='profile',
            name='interest',
            field=models.CharField(blank=True, default='', max_length=1000, verbose_name='Увлечения'),
        ),
        migrations.AddField(
            model_name='profile',
            name='last_name_en',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Фамилия на английском'),
        ),
        migrations.AddField(
            model_name='profile',
            name='nationality',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='Национальность'),
        ),
        migrations.AddField(
            model_name='profile',
            name='skype',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор'),
        ),
        migrations.AddField(
            model_name='resetpassword',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='middle_name',
            field=models.CharField(blank=True, max_length=100, verbose_name='Отчество'),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('is_student', models.BooleanField(default=False, verbose_name='Студент')),
                ('is_teacher', models.BooleanField(default=False, verbose_name='Преподаватель')),
                ('is_org_admin', models.BooleanField(default=False, verbose_name='Администратор организации')),
                ('is_supervisor', models.BooleanField(default=False, verbose_name='Супервизор')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='organizations.Organization', verbose_name='Организация')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='roles', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Роль',
                'verbose_name_plural': 'Роли',
            },
        ),
    ]
