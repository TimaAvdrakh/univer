from django_cron import CronJobBase, Schedule
from . import models
import requests
from portal.current_settings import PASSWORD_RESET_ENDPOINT
from django.utils import timezone


class EmailCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.my_cron_job'  # a unique code

    def do(self):
        print("1 min test")


class PasswordResetUrlSendJob(CronJobBase):
    """Отправляет ссылку для восстановаления пароля на указанный email"""
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron_app.password_reset'  # a unique code

    def do(self):
        tasks = models.ResetPasswordUrlSendTask.objects.filter(is_success=False)
        for item in tasks:
            reset_password = item.reset_password
            data = {
                'email': reset_password.email,
                'user_id': reset_password.user.id,
                'event_date': timezone.now(),
                'forgot_id': reset_password.uuid
            }

            r = requests.post(PASSWORD_RESET_ENDPOINT,
                              data)
            if r.status_code == 200:
                item.is_success = True
                item.save()

