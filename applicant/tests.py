import json
import datetime as dt
from rest_framework.test import APITestCase, APIClient
from organizations.models import PreparationLevel, EducationType
from portal_users.models import PhoneType
from .models import *


# Тестирование бизнес-процесса модуля "Абитуриент"
class ApplicantTestCase(APITestCase):
    # Задаем диапазон создаваемых объектов в тесте
    OBJ_RANGE = range(1, 4)

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
        AdmissionCampaignType.objects.bulk_create([
            AdmissionCampaignType(**campaign_type) for campaign_type in [
                {
                    "name": f"#{obj}",
                    "name_ru": f"#{obj}",
                    "code": f"{obj}",
                } for obj in self.OBJ_RANGE
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
                # 'campaign_type': self.campaign_types.all()[obj - 1],
                # 'prep_level': self.prep_levels.all()[obj - 1],
                'education_type': self.education_types.all()[obj - 1],
                'chosen_directions_max_count': 5,
                'year': str(dt.date.today().year),
                'start_date': dt.date.today(),
                'end_date': dt.date.today() + dt.timedelta(days=90)
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
    
    def setUp(self) -> None:
        super().setUp()
        self.setup_refs()
        self.campaign_types = AdmissionCampaignType.objects.all()
        self.education_types = EducationType.objects.all()
        self.statuses = ApplicationStatus.objects.all()
        self.prep_levels = PreparationLevel.objects.all()
        self.campaigns = AdmissionCampaign.objects.all()

    def test_registration(self):
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'confirm_password': 'test_pass1234',
            'password': 'test_pass1234',
            'email': 'johndoe@gmail.com',
            'doc_num': '88005553535',
            'campaign': self.campaigns.first().uid.__str__(),
            'prep_level': self.prep_levels.objects.first().uid.__str__(),
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
            'email': 'johndoe@gmail.com',
            'phone': {
                'phone_type': 'mobile',
                'value': '88005553535'
            }
        }

    def test_create_admission_application(self):
        pass
