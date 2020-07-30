from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
from common.models import BaseModel

User = get_user_model()


class News(BaseModel):
    title = models.CharField(
        max_length=1000,
        verbose_name='Заголовок'
    )
    content = models.TextField(verbose_name='Контент')
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='news',
        verbose_name='Автор новости'
    )
    is_important = models.BooleanField(
        default=False,
        verbose_name='Важная новость?'
    )
    files = models.ManyToManyField(
        'common.File',
        blank=True,
        verbose_name='Прикрепленные файлы'
    )
    addressees = models.ManyToManyField(
        'portal_users.Profile',
        blank=True,
        verbose_name='Адресаты'
    )
    pub_date = models.DateField(
        verbose_name='Дата публикации',
        default=now,
        blank=True,
    )

    class Meta:
        ordering = ['-pub_date']

    def save(self, *args, **kwargs):
        if self.pub_date < now():
            raise Exception('cannot publish earlier than today')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title[:30]}, Автор {self.author}'
