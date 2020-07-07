# Generated by Django 2.2.4 on 2020-06-30 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicant', '0058_merge_20200625_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='admissioncampaign',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='admissioncampaigntype',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='budgetlevel',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='document1c',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='documentreturnmethod',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='familymembership',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='granttype',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='internationalcerttype',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='privilegetype',
            name='code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
