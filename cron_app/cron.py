from django_cron import CronJobBase, Schedule
from . import models
from django.core.mail import send_mail


class EmailCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'commoncron.my_cron_job'  # a unique code

    def do(self):
        print("1 min test")
        email_tasks = models.EmailTask.objects.filter(is_success=False)
        for item in email_tasks:
            send_mail(item.subject,
                      item.message,
                      from_email='avtoexpertastana@gmail.com',
                      recipient_list=[item.to])
