# Generated by Django 2.2.4 on 2019-09-05 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0020_remove_group_year'),
    ]

    operations = [
        migrations.RenameField(
            model_name='acadperiod',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='acadperiodtype',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='cathedra',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='discipline',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='educationprogram',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='educationtype',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='faculty',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='group',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='language',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='loadtype',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='loadtype2',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='preparationlevel',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='speciality',
            old_name='name_kz',
            new_name='name_kk',
        ),
        migrations.RenameField(
            model_name='studyform',
            old_name='name_kz',
            new_name='name_kk',
        ),
    ]