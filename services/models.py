from django.db import models

# Create your models here.
class Type(models.Model):
        uid = models.CharField(
            max_length=100,
            null=True,
            default='',
            blank=True,
            verbose_name='УИД типа в 1С',
        )
        name = models.TextField(
            default='',
            null=True,
        )

        def __str__(self):
            return '{} - {}'.format(self.name,
                                    self.uid)

        class Meta:
            verbose_name = 'Тип заявки'
            verbose_name_plural = 'Типы заявок'