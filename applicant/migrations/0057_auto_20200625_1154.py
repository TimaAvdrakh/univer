# Generated by Django 2.2.4 on 2020-06-25 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0056_auto_20200619_1634'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='is_orphan',
            field=models.BooleanField(default=False, verbose_name='Является сиротой'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='family',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='questionnaires', to='applicant.Family', verbose_name='Семья'),
        ),
    ]
