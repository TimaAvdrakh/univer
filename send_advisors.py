import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.core.mail import send_mail
from django.template.loader import render_to_string
from portal.curr_settings import current_site
from portal_users.models import UserCredential, Role, Profile
from django.core.files.base import ContentFile
from base64 import b64decode
from organizations import models as org_models
from portal.curr_settings import student_discipline_status, BOT_DEV_CHAT_IDS
# from bot import bot
from django.db import connection
from django.core.mail import send_mail
from django.db.models import Q, Count

# def send():
#     profile_pks = Role.objects.filter(is_supervisor=True).values('profile')
#
#     profiles = Profile.objects.filter(pk__in=profile_pks)
#     for profile in profiles:
#         try:
#             credential = UserCredential.objects.get(user=profile.user)
#
#             msg_plain = render_to_string('emails/credentials_email.txt', {'username': credential.user.username,
#                                                                           'password': credential.password,
#                                                                           'site': current_site})
#             msg_html = render_to_string('emails/credentials_email.html', {'username': credential.user.username,
#                                                                           'password': credential.password,
#                                                                           'site': current_site})
#
#             send_mail(
#                 'Логин и пароль',
#                 msg_plain,
#                 'avtoexpertastana@gmail.com',
#                 [credential.user.profile.email],
#                 html_message=msg_html,
#             )
#
#         except UserCredential.DoesNotExist:
#             pass


# def send_to_profiles():
#     profile_uids = [
#         '5b9dd2e1-1199-11ea-aa49-0cc47a2bc1bf',
#         # 'f48c4ce5-354e-11e9-aa40-0cc47a2bc1bf',
#         # '8633dc89-338f-11e9-aa40-0cc47a2bc1bf',
#         # 'c86915aa-338f-11e9-aa40-0cc47a2bc1bf',
#         # 'a6d87557-338f-11e9-aa40-0cc47a2bc1bf',
#         # 'cc97d130-20b5-11ea-aa49-0cc47a2bc1bf',
#         # '3fa7273c-0755-11ea-aa48-0cc47a2bc1bf',
#         # '2a5974ef-20bc-11ea-aa49-0cc47a2bc1bf',
#         # 'a6df0799-3550-11e9-aa40-0cc47a2bc1bf',
#         # '930481de-338f-11e9-aa40-0cc47a2bc1bf'
#     ]
#
#     profile_pks = Role.objects.filter(is_supervisor=True).values('profile')
#
#     profiles = Profile.objects.filter(pk__in=profile_pks).filter(pk__in=profile_uids)
#
#     for profile in profiles:
#         try:
#             credential = UserCredential.objects.get(user=profile.user)
#
#             msg_plain = render_to_string('emails/credentials_email.txt', {'username': credential.user.username,
#                                                                           'password': credential.password,
#                                                                           'site': current_site})
#             msg_html = render_to_string('emails/credentials_email.html', {'username': credential.user.username,
#                                                                           'password': credential.password,
#                                                                           'site': current_site})
#
#             send_mail(
#                 'Логин и пароль',
#                 msg_plain,
#                 'avtoexpertastana@gmail.com',
#                 [credential.user.profile.email],
#                 html_message=msg_html,
#             )
#
#         except UserCredential.DoesNotExist:
#             pass


# send()
# send_to_profiles()
# print('ok')
#a

import json


# def save_img():
#     with open('D:/test/profile.json') as f:
#         data = json.load(f)
#         value = data['profiles'][0]['avatar']
#         extension = data['profiles'][0]['extension']
#
#     print(value)
#
#     # .encode('utf-8')
#     # data_index = base64_string.index('base64') + 7
#     # filedata = base64_string[data_index:len(base64_string)]
#     image = b64decode(value)
#     p = Profile.objects.get(user__username='odmin')
#
#     setattr(
#         p,
#         'avatar',
#         ContentFile(image, 'odmin20200120.' + extension)
#     )
#     p.save()


# save_img()


def find_dups():
    # dsds = org_models.StudentDiscipline.objects.all().distinct(
    #     'student',
    #     'study_plan_uid_1c',
    #     'acad_period',
    #     'discipline_code',
    #     'discipline',
    #     'load_type',
    #     'hours',
    #     'cycle',
    #     'study_year',
    # )

    query = '''
                SELECT sd.student_id, sd.study_plan_uid_1c, sd.acad_period_id, 
                       sd.discipline_code, sd.discipline_id,
                       sd.load_type_id, sd.hours, sd.cycle_id, sd.study_year_id,
                       COUNT(*) AS dup_count
                FROM organizations_studentdiscipline sd
                WHERE sd.study_year_id = 'c4f1122b-31f5-11e9-aa40-0cc47a2bc1bf'
                GROUP BY sd.student_id, sd.study_plan_uid_1c, sd.acad_period_id, 
                         sd.discipline_code, sd.discipline_id,
                         sd.load_type_id, sd.hours, sd.cycle_id, sd.study_year_id
                HAVING COUNT(*) > 1
            '''

    with connection.cursor() as cursor:
        cursor.execute(query)

        rows = cursor.fetchall()

    for item in rows:
        sds = org_models.StudentDiscipline.objects.filter(
            student=item[0],
            study_plan_uid_1c=item[1],
            acad_period=item[2],
            discipline_code=item[3],
            discipline=item[4],
            load_type=item[5],
            hours=item[6],
            cycle=item[7],
            study_year=item[8],
        )
        print('Dup_num: ', item[9])
        if len(sds) > 1:
            print('Duplicate: {}-{}-{}-{}-{}-{}-{}-{}-{}'.format(
                sds[0].student.user.username,
                sds[0].study_plan_uid_1c,
                sds[0].acad_period.name,
                sds[0].discipline.name,
                sds[0].discipline_code,
                sds[0].load_type.name,
                sds[0].hours,
                sds[0].cycle.name,
                sds[0].study_year.repr_name,
            ))

            uuid1c = None
            for sd in sds:
                if sd.uuid1c is not None:
                    uuid1c = sd.uuid1c

            confirmed_sds = sds.filter(status_id=student_discipline_status['confirmed'])
            changed_sds = sds.filter(status_id=student_discipline_status['changed'])
            rejected_sds = sds.filter(status_id=student_discipline_status['rejected'])
            chosen_sds = sds.filter(status_id=student_discipline_status['chosen'])
            if len(confirmed_sds) > 0:
                for i, each in enumerate(confirmed_sds):
                    if i == 0:
                        each.uuid1c = uuid1c
                        each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['confirmed']).delete()

            elif len(changed_sds) > 0:
                for i, each in enumerate(changed_sds):
                    if i == 0:
                        each.uuid1c = uuid1c
                        each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['changed']).delete()
            elif len(rejected_sds) > 0:
                for i, each in enumerate(rejected_sds):
                    if i == 0:
                        each.uuid1c = uuid1c
                        each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['rejected']).delete()
            elif len(chosen_sds) > 0:
                for i, each in enumerate(chosen_sds):
                    if i == 0:
                        each.uuid1c = uuid1c
                        each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['chosen']).delete()
            else:
                for i, each in enumerate(sds):
                    if i == 0:
                        each.uuid1c = uuid1c
                        each.save()
                    else:
                        each.delete()

    print('Ok')

    # for chat_id in BOT_DEV_CHAT_IDS:
    #     bot.send_message(chat_id,
    #                      'Скрипт закончил работу')


def find_dups_2():
    query = '''
                SELECT sd.student_id, 
                       sd.uuid1c,
                       COUNT(*) AS dup_count
                FROM organizations_studentdiscipline sd
                GROUP BY sd.student_id, sd.uuid1c
                HAVING COUNT(*) > 1
            '''

    with connection.cursor() as cursor:
        cursor.execute(query)

        rows = cursor.fetchall()

    for item in rows:
        sds = org_models.StudentDiscipline.objects.filter(
            student=item[0],
            uuid1c=item[1],
        )
        print('Dup_num: ', item[2])

        if len(sds) > 1:
            print('Duplicate:{}, student: {}, uuid1c: {}'.format(
                item[2],
                sds[0].student.user.username,
                item[1],
                # sds[0].study_plan_uid_1c,
                # sds[0].acad_period.name,
                # sds[0].discipline.name,
                # sds[0].discipline_code,
                # sds[0].load_type.name,
                # sds[0].hours,
                # sds[0].cycle.name,
                # sds[0].study_year.repr_name,
            ))


# find_dups_2()


def to_null():
    sds = org_models.StudentDiscipline.objects.filter(
        uuid1c='',
    )
    for sd in sds:
        print(sd.uid)
        # print('UID 1C:', sd.uuid1c)
        sd.uuid1c = None
        sd.save()
        # print('UID 1C:', sd.uuid1c)
        # print('\n')

    print('To null. ok')


def del_no_uid():
    sds = org_models.StudentDiscipline.objects.filter(
        Q(uuid1c__isnull=True) | Q(uuid1c=''),
        study_year_id='c4f1122b-31f5-11e9-aa40-0cc47a2bc1bf',
    )
    for sd in sds:
        print(sd.uid)
        sd.delete()

    print('no uid delete. ok')


# to_null()
# find_dups()
# del_no_uid()


def find_dups_disc_code():
    # dsds = org_models.StudentDiscipline.objects.all().distinct(
    #     'student',
    #     'study_plan_uid_1c',
    #     'acad_period',
    #     'discipline_code',
    #     'discipline',
    #     'load_type',
    #     'hours',
    #     'cycle',
    #     'study_year',
    # )

    '''
    'student',
    'study_plan',
    'acad_period',
    'discipline',
    'load_type',
    'hours',
    'study_year',
    '''

    query = '''
                SELECT sd.student_id, 
                       sd.study_plan_uid_1c, 
                       sd.acad_period_id, 
                       sd.discipline_id,
                       sd.load_type_id, 
                       sd.hours, 
                       sd.study_year_id,
                       COUNT(*) AS dup_count
                FROM organizations_studentdiscipline sd
                WHERE sd.study_year_id = 'c4f1122b-31f5-11e9-aa40-0cc47a2bc1bf'
                GROUP BY sd.student_id, 
                         sd.study_plan_uid_1c, 
                         sd.acad_period_id, 
                         sd.discipline_id,
                         sd.load_type_id, 
                         sd.hours, 
                         sd.study_year_id
                HAVING COUNT(*) > 1
            '''

    with connection.cursor() as cursor:
        cursor.execute(query)

        rows = cursor.fetchall()

    for item in rows:
        sds = org_models.StudentDiscipline.objects.filter(
            student_id=item[0],
            study_plan_uid_1c=item[1],
            acad_period_id=item[2],
            discipline_id=item[3],
            load_type_id=item[4],
            hours=item[5],
            study_year_id=item[6],
        )
        print('Dup_num: ', item[7])
        if len(sds) > 1:
            print('Duplicate: {}-{}-{}-{}-{}-{}-{}'.format(
                sds[0].student.user.username,
                sds[0].study_plan_uid_1c,
                sds[0].acad_period.name,
                sds[0].discipline.name,
                sds[0].load_type.name,
                sds[0].hours,
                sds[0].study_year.repr_name,
            ))

            uuid1c = None
            for sd in sds:
                if sd.uuid1c is not None and len(sd.uuid1c) > 0:
                    uuid1c = sd.uuid1c
            #
            # confirmed_sds = sds.filter(status_id=student_discipline_status['confirmed'])
            # changed_sds = sds.filter(status_id=student_discipline_status['changed'])
            # rejected_sds = sds.filter(status_id=student_discipline_status['rejected'])
            # chosen_sds = sds.filter(status_id=student_discipline_status['chosen'])

            # if len(confirmed_sds) > 0:
            #     for i, each in enumerate(confirmed_sds):
            #         if i == 0:
            #             each.uuid1c = uuid1c
            #             each.save()
            #         else:
            #             each.delete()
            #     sds.exclude(status_id=student_discipline_status['confirmed']).delete()
            #
            # elif len(changed_sds) > 0:
            #     for i, each in enumerate(changed_sds):
            #         if i == 0:
            #             each.uuid1c = uuid1c
            #             each.save()
            #         else:
            #             each.delete()
            #     sds.exclude(status_id=student_discipline_status['changed']).delete()
            # elif len(rejected_sds) > 0:
            #     for i, each in enumerate(rejected_sds):
            #         if i == 0:
            #             each.uuid1c = uuid1c
            #             each.save()
            #         else:
            #             each.delete()
            #     sds.exclude(status_id=student_discipline_status['rejected']).delete()
            # elif len(chosen_sds) > 0:
            #     for i, each in enumerate(chosen_sds):
            #         if i == 0:
            #             each.uuid1c = uuid1c
            #             each.save()
            #         else:
            #             each.delete()
            #     sds.exclude(status_id=student_discipline_status['chosen']).delete()
            # else:

            for each in sds:
                if each.uuid1c is None or len(each.uuid1c) == 0:
                    each.uuid1c = uuid1c
                    each.save()
                    print('copied!')

    print('Ok')
    send_mail('Script worked',
              'Script is ok',
              'avtoexpertastana@gmail.com',
              ['auganenu@gmail.com'])


# find_dups_disc_code()


def handle_1():
    status_list = [student_discipline_status['confirmed'], student_discipline_status['changed'],
                    student_discipline_status['rejected'], student_discipline_status['chosen']]

    sds_with_uuid1c = org_models.StudentDiscipline.objects.filter(
        uuid1c__isnull=False,
        status_id=student_discipline_status['not_chosen'],
        # student_id='730fdbde-3554-11e9-aa40-0cc47a2bc1bf',
    )
    for item in sds_with_uuid1c:
        print('Duplicate: {}-{}-{}-{}-{}-{}-{}'.format(
            item.student.user.username,
            item.study_plan_uid_1c,
            item.acad_period.name,
            item.discipline.name,
            item.load_type.name,
            item.hours,
            item.study_year.repr_name,
        ))

        duplicates = org_models.StudentDiscipline.objects.filter(
            Q(uuid1c__isnull=True) | Q(uuid1c=''),
            status__pk__in=status_list,
            student=item.student,
            study_plan=item.study_plan,
            discipline=item.discipline,
            load_type=item.load_type,
            hours=item.hours,
            discipline_code=item.discipline_code,
            study_year=item.study_year,
        )
        print(len(duplicates))

        if duplicates.exists():
            duplicate = duplicates.first()

            print('Duplicate: {}-{}-{}-{}-{}-{}-{}'.format(
                duplicate.student.user.username,
                duplicate.study_plan_uid_1c,
                duplicate.acad_period.name,
                duplicate.discipline.name,
                duplicate.load_type.name,
                duplicate.hours,
                duplicate.study_year.repr_name,
            ))

            item.author = duplicate.author
            item.teacher = duplicate.teacher
            item.language = duplicate.language
            item.status = duplicate.status
            item.save()

    print('Ok')
    send_mail('Handle 1',
              'Script is ok',
              'avtoexpertastana@gmail.com',
              ['auganenu@gmail.com'])


def handle_2():
    status_list = [student_discipline_status['confirmed'], student_discipline_status['changed'],
                   student_discipline_status['rejected'], student_discipline_status['chosen']]

    sds_with_uuid1c = org_models.StudentDiscipline.objects.filter(
        uuid1c__isnull=False,
        status_id=student_discipline_status['not_chosen'],
        # student_id='c528659c-1cc3-11ea-aa49-0cc47a2bc1bf',
    )
    for item in sds_with_uuid1c:
        duplicates = org_models.StudentDiscipline.objects.filter(
            Q(uuid1c__isnull=True) | Q(uuid1c=''),
            status__pk__in=status_list,
            student=item.student,
            study_plan=item.study_plan,
            acad_period=item.acad_period,
            discipline=item.discipline,
            load_type=item.load_type,
            discipline_code=item.discipline_code,
            study_year=item.study_year,
        )

        if duplicates.exists():
            duplicate = duplicates.first()

            item.author = duplicate.author
            item.teacher = duplicate.teacher
            item.language = duplicate.language
            item.status = duplicate.status
            item.save()

    print('Ok')
    send_mail('Handle 2',
              'Script is ok',
              'avtoexpertastana@gmail.com',
              ['auganenu@gmail.com'])


handle_1()
handle_2()


def find_dups_with_uid():
    '''
    Удаляет дубликатов по приоритету
    '''

    query = '''
                SELECT   sd.student_id,
                         sd.uuid1c, 
                         sd.study_plan_uid_1c, 
                         sd.acad_period_id,
                         sd.discipline_code,
                         sd.discipline_id,
                         sd.load_type_id, 
                         sd.hours, 
                         sd.study_year_id
                         sd.cycle_id,
                       COUNT(*) AS dup_count
                FROM organizations_studentdiscipline sd
                WHERE sd.study_year_id = 'c4f1122b-31f5-11e9-aa40-0cc47a2bc1bf'
                GROUP BY sd.student_id,
                         sd.uuid1c, 
                         sd.study_plan_uid_1c, 
                         sd.acad_period_id,
                         sd.discipline_code,
                         sd.discipline_id,
                         sd.load_type_id, 
                         sd.hours, 
                         sd.study_year_id,
                         sd.cycle_id,
                HAVING COUNT(*) > 1
            '''

    with connection.cursor() as cursor:
        cursor.execute(query)

        rows = cursor.fetchall()

    for item in rows:
        sds = org_models.StudentDiscipline.objects.filter(
            student_id=item[0],
            uuid1c=item[1],
            study_plan_uid_1c=item[2],
            acad_period_id=item[3],
            discipline_code=item[4],
            discipline_id=item[5],
            load_type_id=item[6],
            hours=item[7],
            study_year_id=item[8],
            cycle_id=item[9],
        )
        print('Dup_num: ', item[10])
        if len(sds) > 1:
            print('Duplicate: {}-{}-{}-{}-{}-{}-{}'.format(
                sds[0].student.user.username,
                sds[0].study_plan_uid_1c,
                sds[0].acad_period.name,
                sds[0].discipline.name,
                sds[0].load_type.name,
                sds[0].hours,
                sds[0].study_year.repr_name,
            ))

            # uuid1c = None
            # for sd in sds:
            #     if sd.uuid1c is not None and len(sd.uuid1c) > 0:
            #         uuid1c = sd.uuid1c

            confirmed_sds = sds.filter(status_id=student_discipline_status['confirmed'])
            changed_sds = sds.filter(status_id=student_discipline_status['changed'])
            rejected_sds = sds.filter(status_id=student_discipline_status['rejected'])
            chosen_sds = sds.filter(status_id=student_discipline_status['chosen'])
            not_chosen_sds = sds.filter(status_id=student_discipline_status['not_chosen'])

            if len(confirmed_sds) > 0:
                for i, each in enumerate(confirmed_sds):
                    if i == 0:
                        pass
                        # each.uuid1c = uuid1c
                        # each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['confirmed']).delete()

            elif len(changed_sds) > 0:
                for i, each in enumerate(changed_sds):
                    if i == 0:
                        pass
                        # each.uuid1c = uuid1c
                        # each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['changed']).delete()
            elif len(rejected_sds) > 0:
                for i, each in enumerate(rejected_sds):
                    if i == 0:
                        pass
                        # each.uuid1c = uuid1c
                        # each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['rejected']).delete()
            elif len(chosen_sds) > 0:
                for i, each in enumerate(chosen_sds):
                    if i == 0:
                        pass
                        # each.uuid1c = uuid1c
                        # each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['chosen']).delete()

    print('Ok')
    send_mail('Script worked',
              'Script is ok',
              'avtoexpertastana@gmail.com',
              ['auganenu@gmail.com'])

