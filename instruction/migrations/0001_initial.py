# Generated by Django 2.2.4 on 2020-07-20 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='instructions/')),
                ('language', models.CharField(choices=[('ru', 'Russian'), ('en', 'English'), ('kz', 'Kazakh')], max_length=2)),
            ],
        ),
    ]
