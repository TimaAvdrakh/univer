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


def save_img():
    with open('D:/test/image.docx') as f:
        value = f.read()
    print(value)

    # .encode('utf-8')
    # data_index = base64_string.index('base64') + 7
    # filedata = base64_string[data_index:len(base64_string)]
    image = b64decode(value)
    p = Profile.objects.get(user__username='odmin')

    setattr(
        p,
        'avatar',
        ContentFile(image, 'odmin2020.jpg')
    )
    p.save()

# 1
save_img()

