# Generated by Django 2.2.4 on 2019-11-26 18:14

from django.db import migrations


# def create_grading_systems(apps, schema_editor):
#     GradingSystem = apps.get_model('schedules', 'GradingSystem')
#     GradingSystem.objects.create(
#         uid='01b43a66-14e0-4836-8062-260f5c5ea14a',
#         name='Стобальная',
#         name_ru='Стобальная',
#         number=1,
#     )
#
#     GradingSystem.objects.create(
#         uid='f9a6c5ad-4ea3-4798-88e4-febb08be7047',
#         name='Двубальная',
#         name_ru='Двубальная',
#         number=2,
#     )


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0014_gradingsystem_number'),
    ]

    operations = [
        # migrations.RunPython(create_grading_systems)
    ]