from django_cron import CronJobBase, Schedule
from . import models
import requests
from portal.curr_settings import PASSWORD_RESET_ENDPOINT, student_discipline_status \
    , component_by_choose_uid, CONTENT_TYPES, SEND_STUD_DISC_1C_URL, BOT_DEV_CHAT_IDS
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from portal.curr_settings import current_site
from portal_users import models as user_models
from organizations import models as org_models
from schedules import models as sh_models
from datetime import datetime, timedelta
from integration.models import DocumentChangeLog
from requests.auth import HTTPBasicAuth
from bot import bot
import json


class EmailCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.my_cron_job'  # a unique code

    def do(self):
        pass


class PasswordResetUrlSendJob(CronJobBase):
    """Отправляет ссылку для восстановаления пароля на указанный email"""
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron_app.password_reset'  # a unique code

    def do(self):
        tasks = models.ResetPasswordUrlSendTask.objects.filter(is_success=False)
        for task in tasks:
            reset_password = task.reset_password

            msg_plain = render_to_string('emails/reset_password/reset_password.txt', {'uid': reset_password.uuid,
                                                                                      'lang': task.lang_code})
            msg_html = render_to_string('emails/reset_password/reset_password.html', {'uid': reset_password.uuid,
                                                                                      'lang': task.lang_code})

            send_mail(
                'Восстановление пароля',
                msg_plain,
                'avtoexpertastana@gmail.com',
                [reset_password.email],
                html_message=msg_html,
            )
            task.is_success = True
            task.save()

            # data = {
            #     'email': reset_password.email,
            #     'user_id': reset_password.user.id,
            #     'event_date': timezone.now(),
            #     'forgot_id': reset_password.uuid
            # }

            # r = requests.post(PASSWORD_RESET_ENDPOINT,
            #                   data)
            # if r.status_code == 200:
            #     item.is_success = True
            #     item.save()


# class SendCredentialsJob(CronJobBase):
#     """Отправляет логин и пароль на email"""
#     RUN_EVERY_MINS = 1
#
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'crop_app.send_credentials'
#
#     def do(self):
#         tasks = models.CredentialsEmailTask.objects.filter(is_success=False)
#         for task in tasks:
#             msg_plain = render_to_string('emails/credentials_email.txt', {'username': task.username,
#                                                                           'password': task.password,
#                                                                           'site': current_site})
#             msg_html = render_to_string('emails/credentials_email.html', {'username': task.username,
#                                                                           'password': task.password,
#                                                                           'site': current_site})
#
#             send_mail(
#                 'Логин и пароль',
#                 msg_plain,
#                 'avtoexpertastana@gmail.com',
#                 [task.to],
#                 html_message=msg_html,
#             )
#             task.is_success = True
#             task.save()


class NotifyAdvisorJob(CronJobBase):
    """Отправляет уведомление Эдвайзеру,
        о завершении выбора студента
    """
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.notify_advisor'

    def do(self):
        mail_subject = 'Студент закончил выбор'
        tasks = models.NotifyAdvisorTask.objects.filter(is_success=False)
        for task in tasks:
            stud_discipline_info = task.stud_discipline_info
            acad_period = stud_discipline_info.acad_period
            study_plan = stud_discipline_info.study_plan
            student = study_plan.student
            advisor = study_plan.advisor

            msg_plain = render_to_string('emails/student_finished_selection.txt',
                                         {'full_name': student.full_name,
                                          'acad_period': acad_period.repr_name}
                                         )
            msg_html = render_to_string('emails/student_finished_selection.html',
                                        {'full_name': student.full_name,
                                         'acad_period': acad_period.repr_name}
                                        )

            send_mail(
                mail_subject,
                msg_plain,
                'avtoexpertastana@gmail.com',
                [advisor.email],
                html_message=msg_html,
            )
            task.is_success = True
            task.save()


class AdvisorRejectBidJob(CronJobBase):
    """Эдвайзер отклонил заявку студента на регистрацию на дисциплины"""

    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.advisor_reject'

    def do(self):
        mail_subject = 'Ваша заявка отклонена'
        tasks = models.AdvisorRejectedBidTask.objects.filter(is_success=False)
        for task in tasks:
            study_plan = task.study_plan
            student = study_plan.student
            advisor = study_plan.advisor

            msg_plain = render_to_string('emails/advisor_reject/advisor_rejected_bid.txt',
                                         {'advisor_name': advisor.full_name,
                                          'comment': task.comment}
                                         )
            msg_html = render_to_string('emails/advisor_reject/advisor_rejected_bid.html',
                                        {'advisor_name': advisor.full_name,
                                         'comment': task.comment}
                                        )

            send_mail(
                mail_subject,
                msg_plain,
                'avtoexpertastana@gmail.com',
                [student.email],
                html_message=msg_html,
            )
            task.is_success = True
            task.save()


class StudPerformanceChangedJob(CronJobBase):
    """Задача для уведомления админов об изменении оценки"""

    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.stud_performance_changed'

    def do(self):
        mail_subject = 'Изменена оценка'
        tasks = models.StudPerformanceChangedTask.objects.filter(is_success=False)
        for task in tasks:
            discipline = task.stud_perf.lesson.discipline

            msg_plain = render_to_string('schedules/email/mark_changed.txt',
                                         {'teacher': task.author.name_initial,
                                          'discipline': discipline.name,
                                          'old_mark': task.old_mark.value_number,
                                          'new_mark': task.new_mark.value_number}
                                         )
            msg_html = render_to_string('schedules/email/mark_changed.html',
                                        {'teacher': task.author.name_initial,
                                         'discipline': discipline.name,
                                         'old_mark': task.old_mark.value_number,
                                         'new_mark': task.new_mark.value_number}
                                        )

            roles = user_models.Role.objects.filter(is_org_admin=True).distinct('profile')

            for role in roles:
                send_mail(
                    mail_subject,
                    msg_plain,
                    'avtoexpertastana@gmail.com',
                    [role.profile.email],
                    html_message=msg_html,
                )
            task.is_success = True
            task.save()


class ControlNotifyJob(CronJobBase):
    """Задача для уведомления студентов о промежуточном контроле"""

    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.control_notify'

    def do(self):
        mail_subject = 'Назначен промежуточный контроль'
        tasks = models.ControlNotifyTask.objects.filter(is_success=False)
        for task in tasks:
            lesson = task.lesson

            date = lesson.date.strftime('%d.%m.%Y')

            groups = lesson.groups.filter(is_active=True)
            study_plans = org_models.StudyPlan.objects.filter(group__in=groups,
                                                              is_active=True)

            msg_plain = render_to_string('schedules/email/control_notify/control_notify.txt',
                                         {'discipline': lesson.discipline.name,
                                          'date': date}
                                         )
            msg_html = render_to_string('schedules/email/control_notify/control_notify.html',
                                        {'discipline': lesson.discipline.name,
                                         'date': date}
                                        )

            for sp in study_plans:
                send_mail(
                    mail_subject,
                    msg_plain,
                    'avtoexpertastana@gmail.com',
                    [sp.student.email],
                    html_message=msg_html,
                )
            task.is_success = True
            task.save()


class CloseLessonsJob(CronJobBase):
    """Закрыть доступ к оцениванию и редактированию Занятии
    в конце недели"""
    RUN_EVERY_MINS = 43200  # every day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.close_lessons_job'

    def do(self):
        lessons = sh_models.Lesson.objects.filter(is_active=True,
                                                  closed=False)
        for lesson in lessons:
            lesson_date = lesson.date
            start = lesson_date - timedelta(days=lesson_date.weekday())
            end = start + timedelta(days=6)

            end_of_week = datetime(year=end.year,
                                   month=end.month,
                                   day=end.day,
                                   hour=23,
                                   minute=59,
                                   second=59)
            now = datetime.now()
            if now >= end_of_week:
                lesson.closed = True
                lesson.save()


class SendStudentDisciplinesTo1CJob(CronJobBase):
    """Отправляет утвержденные Дисциплины студентов в 1С"""
    RUN_EVERY_MINS = 1  # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.send_student_disciplines'

    def do(self):
        url = SEND_STUD_DISC_1C_URL
        status = student_discipline_status['confirmed']
        sds = org_models.StudentDiscipline.objects.filter(
            status_id=status,
            teacher__isnull=False,
            sent=False,
        )[:5]

        disciplines = []
        for sd in sds:
            item = {
                'uid_site': str(sd.uid),  # УИД дисицплины студента на сайте
                'study_plan': sd.study_plan.uid_1c,
                'student': str(sd.student.uid),
                'study_period': str(sd.study_year.uid),
                'advisor': str(sd.study_plan.advisor.uid) if sd.study_plan.advisor else '',
                'acad_period': str(sd.acad_period.uid),
                'teacher': str(sd.teacher.uid),
                'language': str(sd.language.uid),
                'discipline': str(sd.discipline.uid),
                'loadtype': str(sd.load_type.load_type2.uid_1c),
                'isopt': str(sd.component.uid) == component_by_choose_uid if sd.component else False,
            }
            disciplines.append(item)

        resp = requests.post(
            url,
            json=disciplines,
            verify=False,
            auth=HTTPBasicAuth('Администратор'.encode(), 'qwe123rty'),
            timeout=30,
        )

        if resp.status_code == 200:
            resp_data = resp.json()
            for item in resp_data:
                # try:
                #     sent_data = list(filter(lambda disc: disc['uid_site'] == item['uid_site'], disciplines))[0]
                #     sent_data_json = json.dumps(sent_data)
                # except IndexError:
                #     sent_data_json = ''

                log = DocumentChangeLog(
                    content_type_id=CONTENT_TYPES['studentdiscipline'],
                    object_id=item['uid_site'],
                    status=item['code'],
                    # sent_data=sent_data_json,
                )
                error_text = ''
                for error in item['errors']:
                    error_text += '{}\n'.format(error)

                log.errors = error_text
                log.save()

                if item['code'] == 0:
                    try:
                        sd = org_models.StudentDiscipline.objects.get(pk=item['uid_site'])
                    except org_models.StudentDiscipline.DoesNotExist:
                        continue

                    sd.uid_1c = item['uid_1c']
                    sd.sent = True
                    sd.save()
        else:
            message = '{}\n{}'.format(resp.status_code,
                                      resp.content.decode())
            for chat_id in BOT_DEV_CHAT_IDS:
                bot.send_message(chat_id,
                                 message)
