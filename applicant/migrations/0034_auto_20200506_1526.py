# Generated by Django 2.2.4 on 2020-05-06 09:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0121_education_is_nis_graduate'),
        ('applicant', '0033_auto_20200505_1803'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='languageproficiency',
            options={'verbose_name': 'Уровень владения языком (CEFR)', 'verbose_name_plural': 'Уровени владения языками (CEFR)'},
        ),
        migrations.RemoveField(
            model_name='grant',
            name='speciality',
        ),
        migrations.AddField(
            model_name='grant',
            name='edu_program_group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='organizations.EducationProgramGroup', verbose_name='Группа образовательных программ'),
        ),
        migrations.AddField(
            model_name='languageproficiency',
            name='name',
            field=models.CharField(max_length=100, null=True, verbose_name='Натменование уровня'),
        ),
        migrations.AddField(
            model_name='languageproficiency',
            name='name_en',
            field=models.CharField(max_length=100, null=True, verbose_name='Натменование уровня'),
        ),
        migrations.AddField(
            model_name='languageproficiency',
            name='name_kk',
            field=models.CharField(max_length=100, null=True, verbose_name='Натменование уровня'),
        ),
        migrations.AddField(
            model_name='languageproficiency',
            name='name_ru',
            field=models.CharField(max_length=100, null=True, verbose_name='Натменование уровня'),
        ),
        migrations.AlterField(
            model_name='application',
            name='directions',
            field=models.ManyToManyField(to='applicant.RecruitmentPlan', verbose_name='Выборы направлений'),
        ),
        migrations.AlterField(
            model_name='recruitmentplan',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='plans', to='applicant.AdmissionCampaign', verbose_name='Кампания'),
        ),
        migrations.AlterField(
            model_name='recruitmentplan',
            name='prep_direction',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='organizations.Speciality', verbose_name='Направление по подготвке'),
        ),
        migrations.DeleteModel(
            name='DirectionChoice',
        ),
    ]
