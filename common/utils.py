from django.contrib.auth.models import User
import string
import random
from django.core import serializers
import json
from common.models import Log


def get_sentinel_user():
    return User.objects.get_or_create(username='deleted')[0]


def password_generator(size=8, chars=string.ascii_letters + string.digits):
    """
    Returns a string of random characters, useful in generating temporary
    passwords for automated password resets.

    size: default=8; override to provide smaller/larger passwords
    chars: default=A-Za-z0-9; override to provide more/less diversity

    Credit: Ignacio Vasquez-Abrams
    Source: http://stackoverflow.com/a/2257449
    """
    return ''.join(random.choice(chars) for i in range(size))


def make_log(profile, obj):
    """Создать лог"""
    json_data = serializers.serialize("json", [obj])
    model_name = obj.__class__.__name__

    log = Log.objects.create(
        obj_uid=obj.uid,
        model_name=model_name,
        content=json_data,
        profile=profile,
    )
