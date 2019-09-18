# Generated by Django 2.2.4 on 2019-09-18 04:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0036_studentdiscipline_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentdiscipline',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='edited_student_disciplines', to='portal_users.Profile', verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='studentdiscipline',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.Language', verbose_name='Язык'),
        ),
    ]
