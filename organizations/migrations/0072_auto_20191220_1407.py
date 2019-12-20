# Generated by Django 2.2.4 on 2019-12-20 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0049_profile_password_changed'),
        ('organizations', '0071_auto_20191218_1132'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdiscipline',
            name='number',
            field=models.CharField(max_length=100, null=True, verbose_name='Номер учебного плана'),
        ),
        migrations.AlterUniqueTogether(
            name='studyplan',
            unique_together={('student', 'number')},
        ),
    ]