# Generated by Django 2.2.4 on 2020-04-03 05:52

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0115_auto_20200403_1152'),
        ('applicant', '0009_auto_20200402_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='addresstype',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='admissioncampaign',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='applicant',
            name='campaign',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='applicants', to='applicant.AdmissionCampaign'),
        ),
        migrations.AddField(
            model_name='budgetlevel',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='documentreturnmethod',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='familymembership',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='granttype',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='internationalcerttype',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='privilegetype',
            name='code',
            field=models.CharField(blank=True, editable=False, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='AdmissionCampaignType',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('code', models.CharField(blank=True, editable=False, max_length=100, null=True)),
                ('prep_levels', models.ManyToManyField(to='organizations.PreparationLevel', verbose_name='Уровни образования')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='admissioncampaign',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='applicant.AdmissionCampaignType'),
        ),
    ]