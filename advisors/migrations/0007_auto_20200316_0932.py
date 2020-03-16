# Generated by Django 2.2.4 on 2020-03-16 09:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('advisors', '0006_themesoftheses'),
    ]

    operations = [
        migrations.AlterField(
            model_name='themesoftheses',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_themes_theses', to='portal_users.Profile', verbose_name='Обучающийся'),
        ),
    ]
