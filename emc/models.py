from django.db import models
from common.models import BaseModel
from django.contrib.auth.models import User


class EMC(BaseModel):
    name = models.CharField(max_length=250)
    discipline = models.ForeignKey(
        'organizations.Discipline',
        on_delete=models.CASCADE,
        related_name='emcs',
        blank=True, null=True
    )
    language = models.ForeignKey(
        'organizations.Language',
        on_delete=models.CASCADE
    )
    files = models.ManyToManyField(
        'common.File',
        blank=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    description = models.TextField()
