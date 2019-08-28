# Generated by Django 2.2.4 on 2019-08-27 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('is_success', models.BooleanField(default=False, verbose_name='Успешно')),
                ('to', models.EmailField(max_length=254, verbose_name='Email')),
                ('subject', models.CharField(max_length=50, null=True, verbose_name='Заголовок')),
                ('message', models.CharField(max_length=100, null=True, verbose_name='Сообщение')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
