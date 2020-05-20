# Generated by Django 2.2.4 on 2020-02-14 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0053_auto_20200128_1317'),
        ('organizations', '0109_auto_20200210_1748'),
    ]

    operations = [
        migrations.AddField(
            model_name='disciplinecreditcontrolform',
            name='discipline_credit_uuid1c',
            field=models.CharField(max_length=100, null=True, verbose_name='Уид 1С дисциплины кредита'),
        ),
        migrations.AddField(
            model_name='disciplinecreditcontrolform',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='portal_users.Profile', verbose_name='Студент'),
        ),
        migrations.AlterUniqueTogether(
            name='disciplinecreditcontrolform',
            unique_together={('discipline_credit_uuid1c', 'student', 'control_form')},
        ),
    ]