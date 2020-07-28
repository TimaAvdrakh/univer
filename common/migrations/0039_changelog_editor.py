# Generated by Django 2.2.4 on 2020-07-28 01:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0070_profilephone_modified_for_1c'),
        ('common', '0038_identitydocument_modified_for_1c'),
    ]

    operations = [
        migrations.AddField(
            model_name='changelog',
            name='editor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='portal_users.Profile', verbose_name='Пользователь, применивший изменения'),
        ),
    ]
