import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()
import json

from portal_users.models import Profile


profiles = Profile.objects.all()

data = {}

profile_list = []

for profile in profiles:
    profile_list.append(profile.uid)

data['profiles'] = profile_list

with open('profile_data.txt', 'w') as f:
    json.dump(data, f)





