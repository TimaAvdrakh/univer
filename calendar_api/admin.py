from django.contrib import admin
from .models import *
# Register your models here.
models = [
    RepetitionTypes,
    Participants,
    Events,
]

admin.site.register(models)