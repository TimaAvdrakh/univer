from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    class Meta:
        abstract = True

    is_active = models.BooleanField(
        default=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        auto_now=True,
    )
    deleted = models.DateTimeField(
        null=True,
        blank=True,
    )


# class Log(BaseModel):
#     obj_uid = models.CharField()
#     model_name = models.CharField()
#     author = models.ForeignKey(
#         User,
#         on_delete=models.SET()
#     )