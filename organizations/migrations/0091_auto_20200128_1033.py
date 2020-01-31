# Generated by Django 2.2.4 on 2020-01-28 04:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0090_auto_20200124_1350'),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='disciplinecredit',
        #     name='control_form',
        # ),
        migrations.AddField(
            model_name='disciplinecredit',
            name='acad_period',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.AcadPeriod', verbose_name='Акад период'),
        ),
    ]