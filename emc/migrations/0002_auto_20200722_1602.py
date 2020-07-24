# Generated by Django 2.2.4 on 2020-07-22 10:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emc',
            name='discipline',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emcs', to='organizations.Discipline'),
        ),
        migrations.AlterField(
            model_name='emc',
            name='files',
            field=models.ManyToManyField(blank=True, to='common.File'),
        ),
    ]