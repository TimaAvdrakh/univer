import json
import datetime as dt
from rest_framework.test import APITestCase
from common.models import GovernmentAgency
from organizations.models import Organization
from portal_users.models import PhoneType
from .models import *


# Тестирование бизнес-процесса модуля "Абитуриент"
class ApplicantTestCase(APITestCase):
    # Задаем диапазон создаваемых объектов в тесте
    OBJ_RANGE = range(1, 7)
    today = f'{dt.date.today()}'
    period = f'{dt.date.today() + dt.timedelta(days=365)}'

    def setup_refs(self):
        # сетапим справочники
        ApplicationStatus.create_or_update()
        EducationType.objects.bulk_create([
            EducationType(**edu_type) for edu_type in [
                {
                    'name': f'{edu_type}',
                    'name_ru': f'{edu_type}',
                    'name_en': f'{edu_type}',
                    'name_kk': f'{edu_type}',
                } for edu_type in self.OBJ_RANGE
            ]
        ])
        PreparationLevel.objects.bulk_create([
            PreparationLevel(**prep_level) for prep_level in [
                {"shifr": f"6B00000{obj}"} for obj in self.OBJ_RANGE
            ]
        ])
        AdmissionCampaign.objects.bulk_create(
            AdmissionCampaign(**campaign) for campaign in [{
                'name': f"{obj}",
                'name_ru': f'{obj}',
                'education_type': EducationType.objects.all()[obj - 1],
                'chosen_directions_max_count': 5,
                'year': str(dt.date.today().year),
                'start_date': self.today,
                'end_date': self.period
            } for obj in self.OBJ_RANGE]
        )
        PhoneType.objects.bulk_create([
            PhoneType(**phone_type) for phone_type in [
                {
                    'name': f'phone type #{obj}',
                    'name_ru': f'phone type #{obj}',
                    'name_en': f'phone type #{obj}',
                    'name_kk': f'phone type #{obj}',
                } for obj in self.OBJ_RANGE
            ]
        ])
        LanguageProficiency.objects.bulk_create([
            LanguageProficiency(**lp) for lp in [{'code': f'lang prof #{obj}' for obj in self.OBJ_RANGE}]
        ])
        InternationalCertType.objects.bulk_create([
            InternationalCertType(**ict) for ict in [{'name': f'inter cert type #{obj}'} for obj in self.OBJ_RANGE]
        ])
        GrantType.objects.bulk_create([
            GrantType(**gt) for gt in [{'name': f'grant type #{obj}'} for obj in self.OBJ_RANGE]
        ])
        Speciality.objects.bulk_create([
            Speciality(**s) for s in [{'name': f'speciality #{obj}'} for obj in self.OBJ_RANGE]
        ])
        DocScan.objects.bulk_create([
            DocScan(**ds) for ds in [{'name': f'doc scan #{obj}'} for obj in self.OBJ_RANGE]
        ])
        StudyForm.objects.bulk_create([
            StudyForm(**sf) for sf in [{'name': f'study form #{obj}'} for obj in self.OBJ_RANGE]
        ])
        EducationProgram.objects.bulk_create([
            EducationProgram(**ep) for ep in [{'name': f'ed program #{obj}'} for obj in self.OBJ_RANGE]
        ])
        EducationProgramGroup.objects.bulk_create([
            EducationProgramGroup(**epg) for epg in [{'name': f'ed program group #{obj}'} for obj in self.OBJ_RANGE]
        ])
        EducationBase.objects.bulk_create([
            EducationBase(**eb) for eb in [{'name': f'base #{obj}'} for obj in self.OBJ_RANGE]
        ])
        Language.objects.bulk_create([
            Language(**l) for l in [{'name': f'lang {obj}'} for obj in self.OBJ_RANGE]
        ])
        Discipline.objects.bulk_create([
            Discipline(**d) for d in [{'name': f'discipline #{obj}'} for obj in self.OBJ_RANGE]
        ])
        DocumentType.objects.bulk_create([
            DocumentType(**dt) for dt in [{'name': f'doc type #{obj}'} for obj in self.OBJ_RANGE]
        ])
        Organization.objects.bulk_create([
            Organization(**o) for o in [{'name': f'org #{obj}'} for obj in self.OBJ_RANGE]
        ])
        Gender.objects.bulk_create([
            Gender(name='Male', name_en='Male'),
            Gender(name='Female', name_en='Female')
        ])
        MaritalStatus.objects.bulk_create([
            MaritalStatus(**ms) for ms in [{'name': f'ms {obj}'} for obj in self.OBJ_RANGE]
        ])
        Citizenship.objects.bulk_create([
            Citizenship(**c) for c in [{'name': f'citizenship {obj}'} for obj in self.OBJ_RANGE]
        ])
        Nationality.objects.bulk_create([
            Nationality(**n) for n in [{'name': f'nationality {obj}'} for obj in self.OBJ_RANGE]
        ])
        GovernmentAgency.objects.bulk_create([
            GovernmentAgency(**ga) for ga in [{'name': f'Gov agency {obj}'} for obj in self.OBJ_RANGE]
        ])
    
    def setUp(self) -> None:
        super().setUp()
        self._USERNAME = '6B200001'
        self._PASSWORD = 'applicant228'
        self.user = User.objects.create(
            username=self._USERNAME,
            password=self._PASSWORD,
            last_login=self.today
        )
        self.profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            password_changed=True,
            login_sent=True
        )
        self.setup_refs()
        self.campaign_types = AdmissionCampaignType.objects.all()
        self.education_types = EducationType.objects.all()
        self.statuses = ApplicationStatus.objects.all()
        self.prep_levels = PreparationLevel.objects.all()
        self.campaigns = AdmissionCampaign.objects.all()
        self.lang_profs = LanguageProficiency.objects.all()
        self.icts = InternationalCertType.objects.all()
        self.gts = GrantType.objects.all()
        self.specs = Speciality.objects.all()
        self.scans = DocScan.objects.all()
        self.study_forms = StudyForm.objects.all()
        self.ed_programs = EducationProgram.objects.all()
        self.ed_prog_groups = EducationProgramGroup.objects.all()
        self.ed_base = EducationBase.objects.all()
        self.langs = Language.objects.all()
        self.disciplines = Discipline.objects.all()
        self.doc_types = DocumentType.objects.all()
        self.organizations = Organization.objects.all()
        self.genders = Gender.objects.all()
        self.marital_statuses = MaritalStatus.objects.all()
        self.countries = Citizenship.objects.all()
        self.nationalities = Nationality.objects.all()
        self.gov_agencies = GovernmentAgency.objects.all()

    def test_registration(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'middle_name': 'Mr.',
            'confirm_password': 'test_pass1234',
            'password': 'test_pass1234',
            'email': 'johndoe@gmail.com',
            'doc_num': '88005553535',
            'prep_level': self.prep_levels.first().uid.__str__(),
            'consented': True,
        }
        response = self.client.post(
            path='/api/v1/applicant/applicants/',
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = response.data
        self.assertEqual(response.status_code, 201, f"Response fails: {response.status_code}")
        self.assertEqual(response_data["order_number"], 1, f'Order starts from 1, got: {response_data["order_number"]}')
        self.assertIsNotNone(response_data['user'], f"User didn't created, {response_data['user']}")

    def test_create_questionnaire(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'first_name_en': 'John',
            'last_name_en': 'Doe',
            'gender': f'{self.genders.first().uid}',
            'marital_status': f'{self.marital_statuses.first().uid}',
            'citizenship': f'{self.countries.first().uid}',
            'nationality': f'{self.nationalities.first().uid}',
            'workplace': 'TOO "UralGovnoZavod"',
            'position': 'Govnovoz',
            'experience_years': 40,
            'experience_months': 0,
            'birthday': self.today,
            'birthplace': 'Ust\'-Pizduisk',
            'id_doc': {
                'document_type': f'',
                'serial_number': f'',
                'number': f'',
                'given_date': self.today,
                'validity_date': self.period,
                'issued_by': f'{self.gov_agencies.first().uid}'
            },
            'id_doc_scan': f'{self.scans.first().uid}',
            'iin': '88005553535',
            'phone': {
                'phone_type': '',
                'value': '88005553535'
            },
            'email': 'johndoe@gmail.com',
            'address_of_registration': {

            },
            'address_of_residence': '',
            'family': {
                'number_of_children': 3,
                'number_of_young_children': 1,
                'members': [
                    {
                        'first_name': '',
                        'last_name': '',
                        'membership': '',
                        'workplace': '',
                        'position': '',
                        'address': '',
                        'phone': '',
                        'email': '',
                    }
                ]
            }
        }

    def test_create_admission_application(self):
        self.client.login(**{'username': self._USERNAME, 'password': self._PASSWORD})
        data = {
            'previous_education': {
                'document_type': f'{self.doc_types.first().uid}',
                'edu_type': f'{self.education_types.first().uid}',
                'serial_number': '88005553535',
                'number': '14881337228',
                'given_date': self.today,
                'institute': f'{self.organizations.first().uid}',
                'avg_mark': 3.5,
                'study_form': f'{self.study_forms.first().uid}',
                'speciality': f'{self.specs.first().uid}',
                'is_altyn_belgi_holder': False,
                'is_nerd': False,
                'scan': f'{self.scans.first().id}'
            },
            'test_result': {
                'disciplines': [
                    {
                        'discipline': f"{self.disciplines.filter(name__icontains='1').first().uid}",
                        'mark': 40
                    },
                    {
                        'discipline': f"{self.disciplines.filter(name__icontains='2').first().uid}",
                        'mark': 40
                    },
                    {
                        'discipline': f"{self.disciplines.filter(name__icontains='3').first().uid}",
                        'mark': 20
                    },
                    {
                        'discipline': f"{self.disciplines.filter(name__icontains='4').first().uid}",
                        'mark': 10
                    },
                    {
                        'discipline': f"{self.disciplines.filter(name__icontains='5').first().uid}",
                        'mark': 40
                    },
                ],
                'test_certificate': {
                    'number': 123345,
                    'language': f'{self.langs.first().uid}',
                    'issued_at': self.today,
                    'confirmation_document_provided': True,
                    'scan': f'{self.scans.all()[1:2][0].id}'
                }
            },
            'international_cert': {
                'type': f'{self.icts.first().uid}',
                'language_proficiency': f'{self.lang_profs.first().uid}',
                'mark': 6,
                'issued_at': self.today,
                'number': '132125',
            },
            'grant': {
                'type': f'{self.gts.first().uid}',
                'start_date': self.today,
                'end_date': self.period,
                'issued_at': self.today,
                'serial_number': 4124124,
                'number': 152512312,
                'date_of_order': self.today,
                'number_order': 1424123123,
                'speciality': f'{self.specs.first().uid}',
                'scan': f'{self.scans.all()[2:3][0].id}'
            },
            'directions': [
                {
                    'prep_level': f'{self.prep_levels[:1][0].uid}',
                    'study_form': f'{self.study_forms[:1][0].uid}',
                    'education_program': f'{self.ed_programs[:1][0].uid}',
                    'education_program_group': f'{self.ed_prog_groups[:1][0].uid}',
                    'education_base': f'{self.ed_base[:1][0].uid}',
                    'education_language': f'{self.langs[:1][0].uid}'
                },
                {
                    'prep_level': f'{self.prep_levels[:1][0].uid}',
                    'study_form': f'{self.study_forms[:1][0].uid}',
                    'education_program': f'{self.ed_programs[1:2][0].uid}',
                    'education_program_group': f'{self.ed_prog_groups[1:2][0].uid}',
                    'education_base': f'{self.ed_base[1:2][0].uid}',
                    'education_language': f'{self.langs[:1][0].uid}'
                },
                {
                    'prep_level': f'{self.prep_levels[:1][0].uid}',
                    'study_form': f'{self.study_forms[:1][0].uid}',
                    'education_program': f'{self.ed_programs[2:3][0].uid}',
                    'education_program_group': f'{self.ed_prog_groups[2:3][0].uid}',
                    'education_base': f'{self.ed_base[:1][0].uid}',
                    'education_language': f'{self.langs[:1][0].uid}'
                },
            ],
        }
        print(data)
        response = self.client.post(
            path='/api/v1/applicant/applications/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201, f"Request failed, can't create application")
        self.assertEqual(data['status'], AWAITS_VERIFICATION, 'Application is not in queue of verification')
