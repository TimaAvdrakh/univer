# Generated by Django 2.2.4 on 2020-03-06 11:37

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0022_auto_20200128_1538'),
        ('organizations', '0097_remove_disciplinecredit_control_form'),
        ('portal_users', '0054_auto_20200210_2156'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(blank=True, max_length=800, null=True, verbose_name='Name')),
                ('name_ru', models.CharField(blank=True, max_length=800, null=True, verbose_name='Name')),
                ('name_kk', models.CharField(blank=True, max_length=800, null=True, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, max_length=800, null=True, verbose_name='Name')),
                ('street', models.CharField(max_length=500, verbose_name='Street')),
                ('home_number', models.CharField(max_length=500, verbose_name='Home')),
                ('corpus', models.CharField(blank=True, max_length=500, null=True, verbose_name='Corpus')),
                ('apartment', models.CharField(blank=True, max_length=500, null=True, verbose_name='Apartment')),
                ('index', models.CharField(max_length=100, verbose_name='Index')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AddressClassifier',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('address_element_type', models.PositiveSmallIntegerField(verbose_name='Type of address element')),
                ('district_code', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='District code')),
                ('region_code', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Region code')),
                ('locality_code', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Locality code')),
                ('code', models.PositiveSmallIntegerField(verbose_name='Code')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AddressType',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdmissionCampaign',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('use_contest_groups', models.BooleanField(default=False, verbose_name='Use contest groups')),
                ('inter_cert_foreign_lang', models.BooleanField(default=False, verbose_name='International certificate foreign language')),
                ('chosen_direction_max_count', models.PositiveSmallIntegerField(default=0, verbose_name="Maximal count of applicant's chosen directions")),
                ('year', models.CharField(max_length=4, verbose_name='Year of admission')),
                ('start_date', models.DateField(verbose_name='Admission campaign starting date')),
                ('end_date', models.DateField(verbose_name='Admission campaign ending date')),
                ('education_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='organizations.EducationType', verbose_name='')),
            ],
            options={
                'verbose_name': 'Admission campaign',
                'verbose_name_plural': 'Admission campaigns',
            },
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
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('code', models.CharField(blank=True, max_length=10, null=True, verbose_name='Admission campaign type code')),
            ],
            options={
                'verbose_name': 'Admission campaign type',
                'verbose_name_plural': 'Admission campaign types',
            },
        ),
        migrations.CreateModel(
            name='ApplicationStatus',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('code', models.CharField(blank=True, max_length=255, null=True, verbose_name='Code of application status')),
            ],
            options={
                'verbose_name': 'Application status',
                'verbose_name_plural': 'Application statuses',
            },
        ),
        migrations.CreateModel(
            name='DocScan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='media', verbose_name='File')),
                ('path', models.TextField(blank=True, null=True, verbose_name='Path to file')),
                ('ext', models.CharField(blank=True, max_length=20, null=True, verbose_name='File extension')),
                ('name', models.CharField(blank=True, max_length=500, null=True, verbose_name='File name')),
                ('size', models.PositiveIntegerField(blank=True, null=True, verbose_name='File size')),
                ('content_type', models.CharField(blank=True, max_length=500, null=True, verbose_name='Content type of a file')),
            ],
            options={
                'verbose_name': 'Scan of document',
                'verbose_name_plural': 'Scans of documents',
            },
        ),
        migrations.CreateModel(
            name='DocumentReturnMethod',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Family',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('number_of_children', models.PositiveSmallIntegerField(default=0, verbose_name='Number of children')),
                ('number_of_young_children', models.PositiveSmallIntegerField(default=0, verbose_name='Number of underage children')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FamilyMembership',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PrivilegeType',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('name', models.CharField(max_length=800, verbose_name='Название')),
                ('name_ru', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_kk', models.CharField(max_length=800, null=True, verbose_name='Название')),
                ('name_en', models.CharField(max_length=800, null=True, verbose_name='Название')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('first_name_en', models.CharField(max_length=255, verbose_name='English first name')),
                ('last_name_en', models.CharField(max_length=255, verbose_name='English last name')),
                ('workplace', models.CharField(blank=True, max_length=500, null=True, verbose_name='Workplace')),
                ('position', models.CharField(blank=True, max_length=500, null=True, verbose_name='Position')),
                ('experience_years', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Experience in years')),
                ('experience_months', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(12)], verbose_name='Experience in months')),
                ('birthday', models.DateField(verbose_name='Birthday')),
                ('birthplace', models.CharField(max_length=500, verbose_name='Birthplace')),
                ('email', models.EmailField(max_length=100, verbose_name='Email')),
                ('address_of_registration', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='registration_addresses', to='applicant.Address', verbose_name='Address of registration')),
                ('address_of_residence', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='residence_addresses', to='applicant.Address', verbose_name='Address of residence')),
                ('address_of_temp_reg', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='temporary_addresses', to='applicant.Address', verbose_name='Temporary registration address')),
                ('applicant', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='questionnaires', to=settings.AUTH_USER_MODEL, verbose_name='Applicant')),
                ('citizenship', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.Citizenship', verbose_name='Citizenship')),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='questionnaires', to='applicant.Family', verbose_name='Family')),
                ('gender', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='portal_users.Gender', verbose_name='Gender')),
                ('id_doc', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.IdentityDocument', verbose_name='Identity document')),
                ('id_doc_scan', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_id_doc', to='applicant.DocScan', verbose_name='Identification document')),
                ('marital_status', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='portal_users.MaritalStatus', verbose_name='Marital status')),
                ('nationality', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.Nationality', verbose_name='Nationality')),
                ('phone', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='phones', to='portal_users.ProfilePhone', verbose_name='Phone')),
            ],
            options={
                'verbose_name': 'Questionnaire',
                'verbose_name_plural': 'Questionnaires',
            },
        ),
        migrations.CreateModel(
            name='Privilege',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('serial_number', models.CharField(max_length=100, verbose_name='Serial number')),
                ('doc_number', models.CharField(max_length=100, verbose_name='Document number')),
                ('start_date', models.DateField(verbose_name='Start date')),
                ('end_date', models.DateField(verbose_name='End date')),
                ('issued_at', models.DateField(verbose_name='Issued at')),
                ('issued_by', models.CharField(max_length=200, verbose_name='Issued by')),
                ('need_dormitory', models.BooleanField(default=False, verbose_name='Need dormitory to live')),
                ('doc_return_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applicant.DocumentReturnMethod', verbose_name='Document return method')),
                ('doc_type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='common.DocumentType', verbose_name='Type of document')),
                ('questionnaire', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='questionnaires', to='applicant.Questionnaire', verbose_name='Questionnaire link')),
                ('scan', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='applicant.DocScan', verbose_name='Document scan')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='applicant.PrivilegeType', verbose_name='Type of privilege')),
            ],
            options={
                'verbose_name': 'Privilege',
                'verbose_name_plural': 'Privileges',
            },
        ),
        migrations.CreateModel(
            name='FamilyMember',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('first_name', models.CharField(default='', max_length=255, verbose_name='First name')),
                ('last_name', models.CharField(default='', max_length=255, verbose_name='Last name')),
                ('middle_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Middle name')),
                ('workplace', models.CharField(blank=True, max_length=500, null=True)),
                ('position', models.CharField(blank=True, max_length=500, null=True, verbose_name='Position')),
                ('phone', models.CharField(max_length=500, verbose_name='Phone')),
                ('email', models.EmailField(max_length=500, verbose_name='Email')),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='applicant.Address', verbose_name='Address of residence')),
                ('family', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='members', to='applicant.Family', verbose_name='Family')),
                ('membership', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='applicant.FamilyMembership', verbose_name='Membership')),
                ('profile', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.DO_NOTHING, to='portal_users.Profile', verbose_name='Profile')),
            ],
            options={
                'verbose_name': 'Family member',
                'verbose_name_plural': 'Family members',
            },
        ),
        migrations.CreateModel(
            name='CampaignStage',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('start_date', models.DateField(verbose_name='The beginning date of document receipt')),
                ('end_date', models.DateTimeField(verbose_name='The ending date of document receipt')),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='stages', to='applicant.AdmissionCampaign')),
                ('education_base', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='organizations.EducationBase', verbose_name='Education base')),
                ('prep_level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='campaign_stages', to='organizations.PreparationLevel')),
                ('study_form', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='organizations.StudyForm', verbose_name='Study form')),
            ],
            options={
                'verbose_name': 'Campaign stage',
                'verbose_name_plural': 'Campaign stages',
            },
        ),
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('first_name', models.CharField(max_length=100, verbose_name='First name')),
                ('last_name', models.CharField(max_length=100, verbose_name='Last name')),
                ('middle_name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Middle name')),
                ('password', models.CharField(max_length=100, verbose_name='Password')),
                ('confirm_password', models.CharField(max_length=100, verbose_name='Password confirmation')),
                ('email', models.EmailField(max_length=100, verbose_name='Email')),
                ('doc_num', models.CharField(max_length=16, unique=True, verbose_name='Identification document serial number')),
                ('consented', models.BooleanField(default=False, verbose_name='Consent given to process personal data')),
                ('order_number', models.IntegerField(null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(9999)], verbose_name='Order number')),
                ('verified', models.BooleanField(default=False, editable=False, verbose_name='Verified')),
                ('prep_level', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='organizations.PreparationLevel', verbose_name='Preparation level')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='applicant', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Applicant',
                'verbose_name_plural': 'Applicants',
            },
        ),
        migrations.CreateModel(
            name='AdmissionApplication',
            fields=[
                ('uid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='Уникальный идентификатор')),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('sort', models.IntegerField(default=500)),
                ('academic_background', models.CharField(max_length=500, verbose_name='Academic background')),
                ('diploma_num', models.CharField(max_length=100, unique=True, verbose_name='Diploma number')),
                ('grant_num', models.CharField(blank=True, max_length=100, null=True, verbose_name='Grant number')),
                ('grant_order_date', models.DateField(blank=True, null=True, verbose_name='Order date of grant')),
                ('extra_info', models.TextField(blank=True, null=True, verbose_name='Extra information about applicant, like interests and achievements')),
                ('diploma_scan', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_diploma', to='applicant.DocScan', verbose_name='Diploma scan document')),
                ('education_base', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='organizations.EducationBase', verbose_name='Education base')),
                ('ent_results', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='application', to='applicant.DocScan', verbose_name='ENT results')),
                ('files', models.ManyToManyField(blank=True, related_name='application_extra', to='applicant.DocScan', verbose_name='Extra attachments')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='applications', to='applicant.Questionnaire', verbose_name='Applicant form')),
                ('grant_scan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='application_grant', to='applicant.DocScan', verbose_name='Grant scan')),
                ('programs', models.ManyToManyField(to='organizations.EducationProgram', verbose_name='Programs')),
                ('speciality', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='organizations.Speciality', verbose_name='Speciality')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='applications', to='applicant.ApplicationStatus', verbose_name='Application status')),
            ],
            options={
                'verbose_name': 'Admission application',
                'verbose_name_plural': 'Admission applications',
            },
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='cities', to='applicant.AddressClassifier', verbose_name='City'),
        ),
        migrations.AddField(
            model_name='address',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='addresses', to='common.Citizenship', verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='address',
            name='district',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='districts', to='applicant.AddressClassifier', verbose_name='District'),
        ),
        migrations.AddField(
            model_name='address',
            name='locality',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='localities', to='applicant.AddressClassifier', verbose_name='Locality'),
        ),
        migrations.AddField(
            model_name='address',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='addresses', to='portal_users.Profile', verbose_name='Profile'),
        ),
        migrations.AddField(
            model_name='address',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='regions', to='applicant.AddressClassifier', verbose_name='Region'),
        ),
        migrations.AddField(
            model_name='address',
            name='type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='applicant.AddressType', verbose_name='Address type'),
        ),
    ]
