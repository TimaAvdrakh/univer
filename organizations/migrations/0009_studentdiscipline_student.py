# Generated by Django 2.2.4 on 2019-09-03 11:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0008_auto_20190903_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentdiscipline',
            name='student',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='student_disciplines', to=settings.AUTH_USER_MODEL, verbose_name='Студент'),
            preserve_default=False,
        ),
    ]