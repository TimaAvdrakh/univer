# Generated by Django 2.2.4 on 2020-05-06 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0120_remove_disciplinecredit_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='education',
            name='is_NIS_graduate',
            field=models.BooleanField(default=False, verbose_name='Выпускник НИШ'),
        ),
    ]
