# Generated by Django 2.2.4 on 2019-12-11 06:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0035_auto_20191211_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='organizations.Organization', verbose_name='Организация'),
        ),
    ]
