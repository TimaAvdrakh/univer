# Generated by Django 2.2.4 on 2020-05-21 04:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0030_auto_20200521_1056'),
        ('organizations', '0124_auto_20200521_1056'),
        ('applicant', '0040_auto_20200520_1610'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admissiondocument',
            name='files',
        ),
        migrations.RemoveField(
            model_name='grant',
            name='scan',
        ),
        migrations.RemoveField(
            model_name='privilege',
            name='scan',
        ),
        migrations.RemoveField(
            model_name='questionnaire',
            name='id_doc_scan',
        ),
        migrations.RemoveField(
            model_name='testcert',
            name='scan',
        ),
        migrations.AddField(
            model_name='admissiondocument',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.Document', verbose_name='Сканы документов'),
        ),
        migrations.AddField(
            model_name='grant',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.Document', verbose_name='Скан'),
        ),
        migrations.AddField(
            model_name='privilege',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.Document', verbose_name='Скан документа'),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='id_document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='application_id_doc', to='common.Document', verbose_name='Удо скан'),
        ),
        migrations.AddField(
            model_name='testcert',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='common.Document', verbose_name='Скан сертификата'),
        ),
        migrations.DeleteModel(
            name='DocScan',
        ),
    ]
