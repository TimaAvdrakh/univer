import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from django.core.mail import send_mail
from django.template.loader import render_to_string
from portal.curr_settings import current_site
from portal_users.models import UserCredential, Role, Profile


def send():
    profile_pks = Role.objects.filter(is_supervisor=True).values('profile')
    profiles = Profile.objects.filter(pk__in=profile_pks)
    for profile in profiles:
        try:
            credential = UserCredential.objects.get(user=profile.user)

            msg_plain = render_to_string('emails/credentials_email.txt', {'username': credential.user.username,
                                                                          'password': credential.password,
                                                                          'site': current_site})
            msg_html = render_to_string('emails/credentials_email.html', {'username': credential.user.username,
                                                                          'password': credential.password,
                                                                          'site': current_site})

            send_mail(
                'Логин и пароль',
                msg_plain,
                'avtoexpertastana@gmail.com',
                [credential.user.profile.email],
                html_message=msg_html,
            )

        except UserCredential.DoesNotExist:
            pass


send()
print('ok')
