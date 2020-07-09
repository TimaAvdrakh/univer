from django.contrib import admin
from .models import *
# Register your models here.
models = [
    RepetitionTypes,
    Events,
]

admin.site.register(models)