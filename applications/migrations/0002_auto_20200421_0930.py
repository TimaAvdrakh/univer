# Generated by Django 2.2.4 on 2020-04-21 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='application',
            name='comment',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='application',
            name='identity_doc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applications.IdentityDoc', verbose_name='Identity document'),
        ),
        migrations.AlterField(
            model_name='application',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students_profile', to='portal_users.Profile', verbose_name='Профиль'),
        ),
        migrations.AlterField(
            model_name='subapplication',
            name='result_doc',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applications.ServiceDoc', verbose_name='Result document'),
        ),
    ]
