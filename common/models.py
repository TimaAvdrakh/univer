from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from uuid import uuid4


class BaseManager(models.Manager):
    # Эту функцию надо переписать (а лучше не трогать), т.к. неактивные записи также нужны
    def get_queryset(self):
        return super(BaseManager, self).get_queryset().filter(is_active=True)


class BaseModel(models.Model):
    class Meta:
        abstract = True

    uid = models.UUIDField(
        verbose_name='Уникальный идентификатор',
        primary_key=True,
        editable=False,
        default=uuid4,
        unique=True,
    )
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
    sort = models.IntegerField(default=500,)
    exchange = False

    objects = BaseManager()

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return super().__str__()

    def save(self, *args, **kwargs):
        # snapshot - флажок для того чтобы заюзать generic модель Changelog
        # т.е. сохранять историю изменений модели, также предотвращает рекурсивный вызов
        snapshot = kwargs.pop('snapshot', False)
        if snapshot:
            if self.pk:
                # Тащим пока что неизмененную модель и конвертируем ее в словарь
                original = model_to_dict(self._meta.model.objects.get(pk=self.pk))
                # Применили изменения
                super().save(*args, **kwargs)
                # Берем обновленный объект
                updated = self._meta.model.objects.get(pk=self.pk)
                # И тоже конвертируем его в словарь
                updated_dict = model_to_dict(updated)
                # Проходимся по ключам
                for k in original.keys():
                    # Значения ключей не совпадают, значит сохраняем Changelog
                    if original[k] != updated_dict[k]:
                        field = self._meta.get_field(k)
                        if field.many_to_many:
                            original[k] = list(map(lambda x: x.uid, original[k]))
                            updated_dict[k] = list(map(lambda x: x.uid, updated_dict[k]))
                        Changelog.objects.create(
                            content_object=updated,
                            key=k,
                            old_value=original[k],
                            new_value=updated_dict[k]
                        )
        super().save(*args, **kwargs)

    def update(self, src: dict):
        # Для трекинга изменений в моделей за счет словаря со значениями
        for key, value in src.items():
            field = self._meta.get_field(key)
            if field.is_relation and field.many_to_many:
                # если поле M2M, то setattr не прокатит.
                # Нужно тащить само M2M-отношение и сетить (set())
                relation = getattr(self, key)
                relation.set(value)
            else:
                setattr(self, key, value)

    @property
    def diffs(self):
        # тащит изменения
        diffs = Changelog.objects.filter(object_id=self.pk).order_by('-created')
        return diffs

    @property
    def comments(self):
        comments = Comment.objects.filter(object_id=self.pk).order_by('-created')
        return comments


class BaseCatalog(BaseModel):
    # univer = models.ForeignKey(
    #     'organizations.Organization',
    #     on_delete=models.CASCADE,
    #     default=''
    # )
    name = models.CharField(
        max_length=800,
        verbose_name='Название',
    )
    code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class BaseIdModel(models.Model):
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


class Nationality(BaseCatalog):
    class Meta:
        verbose_name = 'Национальность'
        verbose_name_plural = 'Национальности'


class Citizenship(BaseCatalog):
    class Meta:
        verbose_name = 'Гражданство'
        verbose_name_plural = 'Гражданство'


class DocumentTypeGroup(BaseCatalog):
    class Meta:
        verbose_name = 'Группа типов документа'
        verbose_name_plural = 'Группы типов документов'


class DocumentType(BaseCatalog):
    #  Документы абитуриентов
    #  Документы иностранных граждан
    #  Документы об образовании
    #  Паспорта
    #  Регистрация деятельности
    #  Основания приказов
    #  Другие
    group = models.ForeignKey(
        DocumentTypeGroup,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Группа типов',
        related_name='types'
    )

    class Meta:
        verbose_name = 'Тип документа'
        verbose_name_plural = 'Типы документа'


class GovernmentAgency(BaseCatalog):
    class Meta:
        verbose_name = 'Государственная организация'
        verbose_name_plural = 'Государственные организации'


class IdentityDocument(BaseModel):
    profile = models.ForeignKey(
        'portal_users.Profile',
        null=True,
        on_delete=models.CASCADE,
        related_name='identity_documents',
        verbose_name='Пользователь',
    )
    document_type = models.ForeignKey(
        DocumentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name='Тип документа',
    )
    serial_number = models.CharField(
        max_length=100,
        default='',
        blank=True,
        null=True,
        verbose_name='Серия',
    )
    number = models.CharField(
        max_length=100,
        default='',
        blank=True,
        null=True,
        verbose_name='Номер',
    )
    given_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата выдачи',
    )
    validity_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Срок действия',
    )
    issued_by = models.ForeignKey(
        GovernmentAgency,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Кем выдан',
    )
    issued_by_str = models.CharField(
        max_length=1000,
        default='',
        blank=True,
        verbose_name='Кем выдан (строка)',
    )

    def __str__(self):
        return '{}'.format(self.profile.full_name,
                           self.document_type)

    class Meta:
        verbose_name = 'Документ удостоверяющий личность'
        verbose_name_plural = 'Документы удостоверяющий личность'
        unique_together = (
            'profile',
            'document_type',
        )


class RegistrationPeriod(BaseCatalog):
    start_date = models.DateField(
        verbose_name='Дата начала',
    )
    end_date = models.DateField(
        verbose_name='Дата завершения',
    )
    study_year = models.ForeignKey(
        'organizations.StudyPeriod',
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Учебный год',
    )

    def __str__(self):
        return '{}:{}-{}'.format(self.name,
                                 self.start_date,
                                 self.end_date)

    def save(self, *args, **kwargs):
        if self.start_date >= self.end_date:
            """Предупреждение выдавать"""
            pass
        else:
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Период регистрации'
        verbose_name_plural = 'Периоды регистрации'


class CourseAcadPeriodPermission(BaseModel):
    registration_period = models.ForeignKey(
        RegistrationPeriod,
        on_delete=models.CASCADE,
        related_name='course_acad_periods',
        verbose_name='Период регистрации',
    )
    course = models.PositiveSmallIntegerField(
        verbose_name='Курс',
    )
    acad_period = models.ForeignKey(
        'organizations.AcadPeriod',
        on_delete=models.CASCADE,
        verbose_name='Академический период',
    )

    def __str__(self):
        return '{}: {}-{}'.format(self.registration_period,
                                  self.course,
                                  self.acad_period)

    class Meta:
        verbose_name = 'Правила выбора Курс-Акад.период'
        verbose_name_plural = 'Правила выбора Курс-Акад.период'
        unique_together = (
            'course',
            'acad_period',
            'registration_period',
        )


class CreditCoeff(BaseModel):
    start_year = models.PositiveIntegerField(
        verbose_name='Год начала',
    )
    coeff = models.PositiveIntegerField(
        verbose_name='Коэффициент',
    )

    def __str__(self):
        return '{} {}'.format(self.start_year,
                              self.coeff)

    class Meta:
        verbose_name = 'Коэффициент кредита'
        verbose_name_plural = 'Коэффициенты кредитов'
        unique_together = (
            'start_year',
            'coeff',
        )


class Log(BaseModel):
    obj_uid = models.UUIDField()
    model_name = models.CharField(
        max_length=100,
    )
    profile = models.ForeignKey(
        'portal_users.Profile',
        on_delete=models.CASCADE,
        null=True,
        verbose_name='Автор',
        related_name='my_actions',
    )
    date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата'
    )
    content = models.TextField(
        verbose_name='Контент',
    )

    def __str__(self):
        return '{} - {}'.format(self.obj_uid,
                                self.profile.user.username)

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'


class Course(BaseCatalog):
    number = models.IntegerField(
        null=True,
        verbose_name='Номер',
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'


class Comment(BaseModel):
    text = models.TextField('Текст комментария')
    document = models.ForeignKey(
        'Document',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    creator = models.ForeignKey(
        'portal_users.Profile',
        related_name='comments',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.TextField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


# История изменений
class Changelog(BaseModel):
    key = models.CharField(
        'Ключ',
        max_length=300
    )
    old_value = models.CharField(
        'Старое значение',
        max_length=300,
        blank=True,
        null=True,
        default=''
    )
    new_value = models.CharField(
        'Новое значение',
        max_length=300,
        blank=True,
        null=True,
        default=''
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False
    )
    object_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        editable=False,
    )
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )

    class Meta:
        verbose_name = 'Изменения заявления'
        verbose_name_plural = 'Изменения заявлений'


class File(BaseModel):
    name = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Имя файла"
    )
    path = models.FileField(
        verbose_name="Путь к файлу",
        upload_to="upload"
    )
    extension = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Расширение файла"
    )
    size = models.PositiveIntegerField(
        validators=[MaxValueValidator(20971520)],
        blank=True,
        null=True,
        verbose_name="Размер файла"
    )
    content_type = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Тип контента"
    )

    @staticmethod
    # Запись в media
    def handle(file):
        from django.conf import settings
        with open(f"{settings.MEDIA_ROOT}/upload/{file.name}", "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)


class Document(BaseCatalog):
    files = models.ManyToManyField(
        File,
        related_name='document',
        verbose_name='Файлы',
    )

    class Meta:
        verbose_name = 'Документы'
        verbose_name_plural = 'Документы'


class InstitutionConfig(BaseModel):
    """Настройки образовательного учреждения."""
    bg_image = models.FileField(
        upload_to='upload',
        verbose_name='Задний фон',
    )

    class Meta:
        verbose_name = 'Настройки образовательного учреждения'
        verbose_name_plural = 'Настройки образовательных учреждений'

    def __str__(self):
        return 'Настройки ОУ'
