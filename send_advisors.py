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
from portal.curr_settings import student_discipline_status

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
    dsds = org_models.StudentDiscipline.objects.all().distinct(
        'student',
        'study_plan_uid_1c',
        'acad_period',
        'discipline_code',
        'discipline',
        'load_type',
        'hours',
        'cycle',
        'study_year',
    )

    for item in dsds:
        sds = org_models.StudentDiscipline.objects.filter(
            student=item.student,
            study_plan_uid_1c=item.study_plan_uid_1c,
            acad_period=item.acad_period,
            discipline_code=item.discipline_code,
            discipline=item.discipline,
            load_type=item.load_type,
            hours=item.hours,
            cycle=item.cycle,
            study_year=item.study_year,
        )
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

            uuid1c = ''
            for sd in sds:
                if len(sd.uuid1c) > 0:
                    uuid1c = sd.uuid1c

            confirmed_sds = sds.filter(status_id=student_discipline_status['confirmed'])
            if len(confirmed_sds) > 0:
                for i, each in enumerate(confirmed_sds):
                    if i == 0:
                        each.uuid1c = uuid1c
                        each.save()
                    else:
                        each.delete()
                sds.exclude(status_id=student_discipline_status['confirmed']).delete()

            else:
                for i, each in enumerate(sds):
                    if i == 0:
                        each.uuid1c = uuid1c
                        each.save()
                    else:
                        each.delete()

    print('Ok')


find_dups()

# 1