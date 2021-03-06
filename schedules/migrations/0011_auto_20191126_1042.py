# Generated by Django 2.2.4 on 2019-11-26 04:42

from django.db import migrations


def create_journal_statuses(apps, schema_editor):
    JournalStatus = apps.get_model('schedules', 'JournalStatus')

    JournalStatus.objects.create(uid='a74c3c09-e16b-4755-94af-a101eed22767',
                                 name='Не утвержден',
                                 name_ru='Не утвержден',
                                 name_en='Not confirmed',
                                 name_kk='Расталмаган')
    JournalStatus.objects.create(uid='12f7dee5-6133-4999-ae28-6deb71d39477',
                                 name='В Обработке',
                                 name_ru='В Обработке',
                                 name_en='Working',
                                 name_kk='Өнделуде')

    JournalStatus.objects.create(uid='3c245567-7790-4bfd-896f-265f3ef8729b',
                                 name='Утвержден',
                                 name_ru='Утвержден',
                                 name_en='Сonfirmed',
                                 name_kk='Расталган')


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0010_auto_20191126_1042'),
    ]

    operations = [
        migrations.RunPython(create_journal_statuses)
    ]
