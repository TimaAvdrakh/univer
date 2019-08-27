from django.contrib.auth.models import User


def get_sentinel_user():
    return User.objects.get_or_create(username='deleted')[0]
