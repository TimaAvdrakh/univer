# Generated by Django 2.2.4 on 2020-05-07 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0035_application_is_grant_holder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admissiondocument',
            name='recruitment_plan',
        ),
        migrations.RemoveField(
            model_name='application',
            name='admission_document',
        ),
        migrations.RemoveField(
            model_name='application',
            name='questionnaire',
        ),
    ]
