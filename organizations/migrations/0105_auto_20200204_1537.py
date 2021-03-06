# Generated by Django 2.2.4 on 2020-02-04 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0104_auto_20200204_1533'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postrequisite',
            name='uuid1c',
            field=models.CharField(editable=False, max_length=100, null=True, verbose_name='Уид 1С'),
        ),
        migrations.AlterUniqueTogether(
            name='postrequisite',
            unique_together={('study_period', 'discipline', 'available_discipline', 'speciality')},
        ),
    ]
