# Generated by Django 2.2.4 on 2020-05-21 04:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0029_document_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='files',
        ),
        migrations.AddField(
            model_name='comment',
            name='document',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.Document'),
        ),
    ]