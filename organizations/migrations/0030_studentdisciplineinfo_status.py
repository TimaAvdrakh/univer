# Generated by Django 2.2.4 on 2019-09-10 05:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0029_auto_20190910_1121'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdisciplineinfo',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organizations.StudentDisciplineInfoStatus', verbose_name='Статус'),
        ),
    ]
