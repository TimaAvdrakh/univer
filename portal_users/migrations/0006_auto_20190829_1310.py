# Generated by Django 2.2.4 on 2019-08-29 07:10

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('portal_users', '0005_organizationtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationtoken',
            name='token',
            field=models.CharField(default=uuid.uuid4, max_length=40, verbose_name='Токен'),
        ),
    ]