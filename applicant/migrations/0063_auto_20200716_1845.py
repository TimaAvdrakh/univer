# Generated by Django 2.2.4 on 2020-07-16 12:45

from django.db import migrations, models
import django.db.models.deletion


def move_phones_to_m2m(apps, schema_editor):
    Questionnaire = apps.get_model('applicant', 'Questionnaire')
    for questionnaire in Questionnaire.objects.all():
        questionnaire.phones.add(questionnaire.phone)
        questionnaire.save()


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0067_auto_20200630_1352'),
        ('applicant', '0062_questionnaire_phone2'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionnaire',
            name='phones',
            field=models.ManyToManyField(blank=True, related_name='questionnaires', to='portal_users.ProfilePhone', verbose_name='Телефоны'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='address_of_temp_reg',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='temporary_addresses', to='applicant.Address', verbose_name='Адрес временной регистрации'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='creator',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='portal_users.Profile', verbose_name='Подающий анкету'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='doc_return_method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='applicant.DocumentReturnMethod', verbose_name='Метод возврата документов'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='family',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='questionnaires', to='applicant.Family', verbose_name='Семья'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='marital_status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portal_users.MaritalStatus', verbose_name='Семейное положение'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='phone2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portal_users.ProfilePhone', verbose_name='Телефон дополнительный'),
        ),
        migrations.RunPython(move_phones_to_m2m),
    ]
