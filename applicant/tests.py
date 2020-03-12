import json
import datetime as dt
from rest_framework.test import APITestCase, APIClient
from .models import *


# Тестирование бизнес-процесса модуля "Абитуриент"
class ApplicantTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        # сетапим справочники
        campaign_types = [
            {
                "name": f"#{obj}",
                "name_ru": f"#{obj}",
                "code": f"{obj}",
            } for obj in range(1, 4)
        ]
        AdmissionCampaignType.objects.bulk_create([
            AdmissionCampaignType(**campaign_type) for campaign_type in campaign_types
        ])
        self.campaign_types = AdmissionCampaignType.objects.all()
        ApplicationStatus.create_or_update()
        self.statuses = ApplicationStatus.objects.all()

        prep_levels = [
            {"shifr": f"6B00000{obj}"} for obj in range(1, 4)
        ]
        PreparationLevel.objects.bulk_create([
            PreparationLevel(**prep_level) for prep_level in prep_levels
        ])
        self.prep_levels = PreparationLevel.objects.all()

        campaigns = [{
            'name': f"{obj}",
            'name_ru': f'{obj}',
            'campaign_type': self.campaign_types.all()[obj - 1],
            'prep_level': self.prep_levels.all()[obj - 1],
            'start_date': dt.date.today(),
            'end_date': dt.date.today() + dt.timedelta(days=90)
        } for obj in range(1, 4)]
        AdmissionCampaign.objects.bulk_create(
            AdmissionCampaign(**campaign) for campaign in campaigns
        )
        self.campaigns = AdmissionCampaign.objects.all()

    def test_registration(self):
        # Ебучие uidы
        first_campaign = self.campaigns.first()

        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'test_pass1234',
            'email': 'johndoe@gmail.com',
            'serial_number': '88005553535',
            'campaign': str(first_campaign.uid),
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
        pass

    def test_create_admission_application(self):
        pass
