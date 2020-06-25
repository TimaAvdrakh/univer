import datetime as dt
from django_cron import CronJobBase, Schedule
from . import models
import requests
from portal.curr_settings import (
    student_discipline_status,
    component_by_choose_uid,
    CONTENT_TYPES,
    SEND_STUD_DISC_1C_URL,
    SEND_APPLICATIONS_TO_1C_URL,
    BOT_DEV_CHAT_IDS
)
from portal.local_settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.template.loader import render_to_string
from portal.curr_settings import current_site
from portal_users import models as user_models
from organizations import models as org_models
from schedules import models as sh_models
from datetime import datetime, timedelta
from django.utils import timezone
from integration.models import DocumentChangeLog
from requests.auth import HTTPBasicAuth
from bot import bot
import json
from reports import views as report_views
from advisors import views as advisor_views
from common import models as common_models
import urllib3
import certifi
from applicant.models import Applicant
from applications import models as model_aps


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
                                                                                      'lang': task.lang_code,
                                                                                      'site': current_site})
            msg_html = render_to_string('emails/reset_password/reset_password.html', {'uid': reset_password.uuid,
                                                                                      'lang': task.lang_code,
                                                                                      'site': current_site})

            send_mail(
                'Восстановление пароля',
                msg_plain,
                EMAIL_HOST_USER,
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
        tasks = models.AdvisorRejectedBidTask.objects.filter(
            is_success=False,
        )
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
            if student.notify_me_from_email:
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
                if sp.student.notify_me_from_email:
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
        )[0]
        sds = org_models.StudentDiscipline.objects.filter(
            status_id=status,
            teacher__isnull=False,
            sent=False,
            student=sds.student
        )
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
        urllib3.disable_warnings()
        resp = requests.post(
            url,
            json=disciplines,
            verify=False,
            auth=HTTPBasicAuth('Администратор'.encode(), 'qwe123rty'),
            timeout=30,
        )

        if resp.status_code == 200:
            print("Connected")
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
                    # sent_data=item['json'],
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


class SendConfirmedDisciplineCreditTo1CJob(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron_app.send_discipline_credit'

    def do(self):
        url = SEND_STUD_DISC_1C_URL
        status = student_discipline_status['confirmed']
        # dcs = org_models.DisciplineCredit.objects.filter(
        #     status_id=status,
        #     uuid1c__isnull=False,
        #     sent=False,
        #     chosen_control_forms__isnull=False,
        #     acad_period__isnull=False,
        #     student__isnull=False
        # )[:3]
        dcs = org_models.DisciplineCredit.objects.filter(
            student='89f4f1ac-355d-11e9-aa40-0cc47a2bc1bf',
            status_id=status,
        )

        discredits = []
        for dc in dcs:
            student_discipline_study_period = org_models.StudentDiscipline.objects.get(
                status=dc.status,
                student=dc.student.uid,
                acad_period=dc.acad_period.uid,
                discipline=dc.discipline.uid,
            )
            for control_form in dc.chosen_control_forms.all():
                item = {
                    'blocktype': 'disciplinecredit',
                    'uid_site': str(dc.uid),
                    'discipline': str(dc.discipline.uid),
                    'cycle': str(dc.cycle.uid),
                    'credit': str(dc.credit),
                    'acad_period': str(dc.acad_period.uid),
                    'chosen_control_forms': str(control_form.uid),
                    'student': str(dc.student.uid),
                    'study_plan_uid_1c': str(dc.study_plan_uid_1c),
                    'study_period': str(student_discipline_study_period.study_year.uid),
                }
                discredits.append(item)
        urllib3.disable_warnings()
        # with open('data.json', 'w') as outfile:
        #     json.dump(discredits, outfile, indent=1)
        resp = requests.post(
            url,
            json=discredits,
            verify=False,
            auth=HTTPBasicAuth('Администратор'.encode(), 'qwe123rty'),
            timeout=30,
        )
        if resp.status_code == 200:
            resp_data = resp.json()
            for item in resp_data:
                log = DocumentChangeLog(
                    content_type_id=CONTENT_TYPES['disciplinecredit'],
                    object_id=item['uid_site'],
                    status=item['code'],
                )
                error_text = ''
                for error in item['errors']:
                    error_text += '{}\n'.format(error)

                log.errors = error_text
                log.save()

                if item['code'] == 0:
                    try:
                        sd = org_models.DisciplineCredit.objects.get(pk=item['uid_site'])
                    except org_models.DisciplineCredit.DoesNotExist:
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


class SendConfirmedThemesOfTheses(CronJobBase):
    pass
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron_app.send_student_themes_of_thesis'

    def do(self):
        url = SEND_STUD_DISC_1C_URL
        tots = ad_models.ThemesOfTheses.objects.filter(
            student__isnull=False,
        )[:5]
        themes = []
        for tot in tots:
            item = {
                'uid_site': str(tot.uid),
                'student': str(tot.student.uid),
            }
            themes.append(item)
        urllib3.disable_warnings()
        resp = requests.post(
            url,
            json=themes,
            verify=False,
            auth=HTTPBasicAuth('Администратор'.encode(), 'qwe123rty'),
            timeout=30,
        )

        if resp.status_code == 200:
            print("Connected")
            resp_data = resp.json()
            for item in resp_data:
                log = DocumentChangeLog(
                    content_type_id=CONTENT_TYPES['themesofthesis'],
                    object_id=item['uid_site'],
                    status=item['code'],
                )
                error_text = ''
                for error in item['errors']:
                    error_text += '{}\n'.format(error)

                log.errors = error_text
                log.save()

                if item['code'] == 0:
                    try:
                        sd = ad_models.ThemesOfTheses.objects.get(pk=item['uid_site'])
                    except ad_models.ThemesOfTheses.DoesNotExist:
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


class ClosePlannedJournalJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.close_planned_journal'  # a unique code

    def do(self):
        tasks = models.PlanCloseJournalTask.objects.filter(is_success=False)[:10]
        for task in tasks:
            now = datetime.now()
            if now >= task.date_time:
                for journal in task.journals.filter(is_active=True):
                    journal.closed = True
                    journal.block_date = datetime.now()
                    journal.save()
                    journal.close_lessons()
                task.is_success = True
                task.save()


class GenerateExcelJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.generate_excel'  # a unique code

    def do(self):
        tasks = models.ExcelTask.objects.filter(is_success=False)[:3]
        for task in tasks:
            doc_type = task.doc_type

            # DOC_TYPE_CHOICES = (
            #     (1, 'Результат регистрации'),
            #     (2, 'Статистика регистрации '),
            #     (3, 'Список незарегистрированных'),
            #     (4, 'Заявки на ИУПЫ обуч'),
            #     (5, 'ИУПЫ обуч'),
            # )

            handler = {
                1: report_views.make_register_result_rxcel,
                2: report_views.make_register_statistics_excel,
                3: report_views.make_not_registered_student_excel,
                4: advisor_views.make_iup_bid_excel,
                5: advisor_views.make_iup_excel,
            }
            handler[doc_type](task)
            task.is_success = True
            task.save()


# class DeleteDuplicateJob(CronJobBase):
#     RUN_EVERY_MINS = 1  # every 1 min
#
#     schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
#     code = 'crop_app.delete_duplicate'  # a unique code
#
#     def do(self):
#         sd_bool = not org_models.StudentDiscipline.objects.filter(uuid1c='').exists()
#         td_bool = not org_models.TeacherDiscipline.objects.filter(uuid1c='').exists()
#
#         if sd_bool and td_bool:
#             for chat_id in BOT_DEV_CHAT_IDS:
#                 bot.send_message(chat_id,
#                                  'Дубликаты удалены')
#
#         tds = org_models.TeacherDiscipline.objects.filter(uuid1c='')[:50]
#         for td in tds:
#             td.delete()
#
#         sds = org_models.StudentDiscipline.objects.filter(uuid1c='')[:50]
#         for sd in sds:
#             sd.delete()
#
#         # pres = models_organizations.Prerequisite.objects.filter(uuid1c='')
#         # for pre in pres:
#         #     pre.delete()
#
#         # posts = models_organizations.Postrequisite.objects.filter(uuid1c='')
#         # for post in posts:
#         #     post.delete()
#


class NotifyStudentToRegisterJob(CronJobBase):
    """Уведомление студентам на почту во время регистрации на дисциплины"""
    RUN_EVERY_MINS = 1  # every 1 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.notify_student_to_register'

    def do(self):
        today = datetime.today()
        reg_periods = common_models.RegistrationPeriod.objects.filter(
            end_date__gte=today,
            is_active=True,
        ).values('study_year')

        # org_models.StudentDiscipline.objects.filter(study)


class ApplicantVerificationJob(CronJobBase):
    """
    Удаляет неактивных абитуриентов, которые не подтвердили свою регистрацию по почте
    """
    RUN_DAILY = 24 * 60
    RUN_AT_TIMES = ['00:00']

    schedule = Schedule(run_every_mins=RUN_DAILY)
    code = 'cron_app.applicant_verification_job'

    def do(self):
        Applicant.erase_inactive()


class SendApplicationsTo1cJob(CronJobBase):
    """Отправляет заявки студентов в 1С"""
    RUN_EVERY_MINS = 10  # every 10 min

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cron_app.send_student_application'

    LANG_EN = '789cb6fa-31e9-11e9-aa40-0cc47a2bc1bf'
    LANG_KZ = '789cb6fb-31e9-11e9-aa40-0cc47a2bc1bf'
    LANG_RU = '789cb6fc-31e9-11e9-aa40-0cc47a2bc1bf'

    IN_PROGRESS = 'b287ecfe-0ac8-499b-9ac4-7da2a64a82ef'

    def do(self):
        # Todo Если получение справки то документ не нужен
        sub_apps = model_aps.SubApplication.objects.filter(application__send=False).values(
            'application', 'application__type__uid', 'status', 'subtype_id', 'comment', 'id',
            'application__profile__uid',
            'organization', 'is_paper', 'copies', 'lang')
        applications = sub_apps.values('application').distinct().values(
            'application', 'application__type_id', 'application__profile__uid')

        sub_apps = list(sub_apps)
        apps_json = []
        url = SEND_APPLICATIONS_TO_1C_URL
        for app in applications:
            sub_app_by_app = [item for item in sub_apps if item['application'] == app['application']]
            sub_json = []
            for sub_application in sub_app_by_app:
                lang_list = []
                for lang in sub_application['lang']:
                    if lang == 'ru':
                        lang_list.append(self.LANG_RU)
                    if lang == 'kz':
                        lang_list.append(self.LANG_KZ)
                    if lang == 'en':
                        lang_list.append(self.LANG_EN)

                sub_item = {
                    "applicationSubtypeID": str(sub_application['subtype_id']),
                    "subApplicationID": sub_application['id'],
                    "organizationName": sub_application['organization'],
                    "isPaper": sub_application['is_paper'],
                    "copyNumber": sub_application['copies'],
                    "lang": lang_list
                }
                sub_json.append(sub_item)
            item = {
                "applicationID": app['application'],
                "applicationType": str(app['application__type_id']),
                "applicationScan": "file_name",
                "applicationStudent": str(app['application__profile__uid']),
                "applicationSubtype": sub_json
            }
            apps_json.append(item)
        urllib3.disable_warnings()
        resp = requests.post(
            url,
            json=apps_json,
            verify=False,
            auth=HTTPBasicAuth('Администратор'.encode(), 'qwe123rty'),
            timeout=30,
        )

        if resp.status_code == 200:
            resp_data = resp.json()

            for application in resp_data:
                status = application['status']
                if status == 'errors':
                    status = 2
                if status == 'success':
                    status = 0
                if status == 'failed':
                    status = 1

                log = DocumentChangeLog(
                    content_type_id=CONTENT_TYPES['applications'],
                    object_id=application['applicationID'],
                    status=status,
                )
                error_text = ''

                for error in application['applicationErrors']:
                    error_text += '{}\n'.format(error)
                for subtype in application['subtypeAplications']:
                    error_text += '\n Дочерний тип заявки ' + str(subtype['subApplicationID'])
                    if subtype['status'] == 'errors':
                        for error in subtype['subApplicationErrors']:
                            error_text += '{}\n'.format(error)
                    if subtype['status'] != 'failed':
                        try:
                            subtype_row = model_aps.SubApplication.objects.get(pk=subtype['subApplicationID'])
                        except model_aps.SubApplication.DoesNotExist:
                            error_text += '{}\n Дочерний тип '+ subtype['subApplicationID'] + ' заявки не найден'
                            continue
                        subtype_row.status = model_aps.Status.objects.only('uid').get(uid=self.IN_PROGRESS)
                        subtype_row.save()

                log.errors = error_text
                log.save()

                if application['status'] == 'success':
                    try:
                        application_row = model_aps.Application.objects.get(pk=application['applicationID'])
                    except model_aps.Application.DoesNotExist:
                        error_text += '{}\n Заявка ' + application['applicationID'] + ' не найдена'
                        continue

                    application_row.send = True
                    application_row.save()

        else:
            message = '{}\n{}'.format(resp.status_code,
                                      resp.content.decode())
            for chat_id in BOT_DEV_CHAT_IDS:
                bot.send_message(chat_id,
                                 message)


class CloseApplicationsJob(CronJobBase):
    """Закрыть доступ к справкам через неделю после выполнения"""
    RUN_EVERY_MINS = 1440  # every day

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'crop_app.close_applications_job' # an unique code

    def do(self):
        rows = model_aps.SubApplication.objects.filter(
            status__code=model_aps.COMPLETED,
            completed_date__lte=(timezone.now() - timedelta(days=7))
        )

        completed_status = model_aps.Status.objects.get(code=model_aps.OUTDATED)
        for application in rows:
            application.status = completed_status
            application.save()