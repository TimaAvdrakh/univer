# Generated by Django 2.2.4 on 2020-03-13 04:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0003_remove_applicant_verified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='privilege',
            name='need_dormitory',
        ),
        migrations.RemoveField(
            model_name='privilege',
            name='questionnaire',
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='address_of_registration',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='registration_addresses', to='applicant.Address', verbose_name='Address of registration'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='address_of_residence',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='residence_addresses', to='applicant.Address', verbose_name='Address of residence'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='address_of_temp_reg',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='temporary_addresses', to='applicant.Address', verbose_name='Temporary registration address'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='applicant',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='questionnaires', to=settings.AUTH_USER_MODEL, verbose_name='Applicant'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='family',
            field=models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='questionnaires', to='applicant.Family', verbose_name='Family'),
        ),
        migrations.CreateModel(
            name='UserPrivilegeList',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('need_dormitory', models.BooleanField(default=False, verbose_name='Need dormitory to live')),
                ('questionnaire', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='applicant.Questionnaire', verbose_name='Questionnaire')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='privilege',
            name='list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='privileges', to='applicant.UserPrivilegeList', verbose_name='User privilege'),
        ),
    ]
