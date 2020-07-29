from django.contrib.auth import get_user_model
from django.db import models
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

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.title[:30]}, Автор {self.author}'
