from django.core.management import call_command
from ddf import G
import pytest
from applicant.models import Applicant


@pytest.mark.django_db
def test_applicant_verification_cron_job():
    new_applicant = G(Applicant)
    call_command("runcrons")
    applicants = Applicant.objects.count()
    assert applicants == 0
