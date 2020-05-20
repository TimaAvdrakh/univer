# Generated by Django 2.2.4 on 2020-05-05 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0031_questionnaire_is_experienced'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='admissioncampaigntype',
            options={'verbose_name': 'Тип приемной кампании', 'verbose_name_plural': 'Типы приемных кампаний'},
        ),
        migrations.AddField(
            model_name='address',
            name='address_matches',
            field=models.CharField(blank=True, choices=[(0, 'registration'), (1, 'temporary registration'), (2, 'residence'), (3, 'does not match')], max_length=1, null=True, verbose_name='Адрес соответствует'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='address_matches',
            field=models.CharField(blank=True, choices=[(0, 'registration address'), (1, 'temporary registration address')], max_length=1, null=True, verbose_name='Адресу фактического проживания соответствует'),
        ),
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.CharField(blank=True, choices=[(0, 'address of registration'), (1, 'address of temporary registration'), (2, 'address of residence')], max_length=1, null=True, verbose_name='Тип адреса'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='id_doc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.IdentityDocument', verbose_name='Удостоверение личности'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='iin',
            field=models.CharField(max_length=12, null=True, verbose_name='ИИН'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='is_experienced',
            field=models.BooleanField(default=False, verbose_name='Имеет опыт работы'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='middle_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Отчество'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='need_dormitory',
            field=models.BooleanField(default=False, verbose_name='Нуждается в общежитии'),
        ),
        migrations.DeleteModel(
            name='AddressType',
        ),
    ]