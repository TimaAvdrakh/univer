# Generated by Django 2.2.4 on 2019-10-30 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0003_auto_20191024_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='advisorcheck',
            name='status',
            field=models.IntegerField(choices=[(3, 'Отклонено'), (4, 'Утверждено'), (5, 'Изменено')]),
        ),
    ]
