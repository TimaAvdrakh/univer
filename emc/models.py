from django.db import models
from common.models import BaseModel
from django.contrib.auth.models import User


class EMC(BaseModel):
    discipline = models.ForeignKey(
        'organizations.Discipline',
        on_delete=models.CASCADE
    )
    language = models.ForeignKey(
        'organizations.Language',
        on_delete=models.CASCADE
    )
    files = models.ManyToManyField(
        'common.File'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    description = models.TextField()
