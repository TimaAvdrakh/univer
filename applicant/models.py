import datetime as dt
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMessage, send_mail
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Case, When, Value, Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from common.models import (
    BaseModel,
    BaseCatalog,
    Comment,
    IdentityDocument,
    Citizenship,
    Nationality,
    Changelog,
)
from portal_users.models import Profile, ProfilePhone, Gender, MaritalStatus, Role
from organizations.models import (
    PreparationLevel,
    Speciality,
    EducationProgram,
    StudyForm,
    StudyPeriod,
    Education,
    EducationType,
    EducationBase,
    EducationProgramGroup,
    Cathedra,
    ControlForm,
    Discipline,
    Language,
)
from organizations.models import DocumentType


APPROVED = "APPROVED"
REJECTED = "REJECTED"
AWAITS_VERIFICATION = "AWAITS_VERIFICATION"
NO_QUESTIONNAIRE = "NO_QUESTIONNAIRE"

COND_ORDER = Case(
    When(Q(status__code=AWAITS_VERIFICATION), then=Value(0)),
    When(Q(status__code=NO_QUESTIONNAIRE), then=Value(1)),
    default=Value(0),
    output_field=models.IntegerField(),
)


# Вид льготы
class PrivilegeType(BaseCatalog):
    class Meta:
        verbose_name = "Тип льготы"
        verbose_name_plural = "Типы льготы"


# Способ возврата документа
class DocumentReturnMethod(BaseCatalog):
    class Meta:
        verbose_name = "Метод возврата документа"
        verbose_name_plural = "Методы возврата документов"


# Членство в семье
class FamilyMembership(BaseCatalog):
    class Meta:
        verbose_name = "Степень родства"
        verbose_name_plural = "Степени родства"


# Уровни бюджета
class BudgetLevel(BaseCatalog):
    class Meta:
        verbose_name = "Уровень бюджета"
        verbose_name_plural = "Уровни бюджета"


# Тип международного сертификата
class InternationalCertType(BaseCatalog):
    class Meta:
        verbose_name = "Тип международного сертификата"
        verbose_name_plural = "Типы международных сертификатов"


# Тип гранта
class GrantType(BaseCatalog):
    class Meta:
        verbose_name = "Вид гранта"
        verbose_name_plural = "Виды грантов"


# Адресный классификатор
class AddressClassifier(BaseCatalog):
    address_element_type = models.PositiveIntegerField(
        verbose_name="Тип адресного элемента"
    )
    district_code = models.PositiveIntegerField(
        verbose_name="Код района",
        blank=True,
        null=True
    )
    region_code = models.PositiveIntegerField(
        verbose_name="Код региона",
        blank=True,
        null=True
    )
    locality_code = models.PositiveIntegerField(
        verbose_name="Код населенного пункта",
        blank=True,
        null=True  # Населенный пункт
    )
    code = models.PositiveIntegerField(
        verbose_name="Код",
        unique=True
    )

    class Meta:
        verbose_name = "Адресный классификатор"
        verbose_name_plural = "Адресные классификаторы"


# Адрес пользователя
class Address(BaseCatalog):
    REG = 0  # Адрес регистрации/прописки
    TMP = 1  # Адрес времменной регистрации
    RES = 2  # Адрес фактического проживания
    ADDRESS_TYPE_CHOICES = (
        (REG, _('address of registration')),
        (TMP, _('address of temporary registration')),
        (RES, _('address of residence'))
    )
    name = models.CharField(
        blank=True,
        null=True,
        max_length=800,
        verbose_name="Имя",
    )
    type = models.CharField(
        max_length=1,
        choices=ADDRESS_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Тип адреса'
    )
    profiles = models.ManyToManyField(
        Profile,
        blank=True,
        verbose_name="Профили",
        related_name="addresses",
    )
    country = models.ForeignKey(
        Citizenship,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Страна",
        related_name="addresses",
    )
    city = models.ForeignKey(
        AddressClassifier,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Город",
        related_name="cities",
    )
    region = models.ForeignKey(
        AddressClassifier,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Регион",
        related_name="regions",
    )
    locality = models.ForeignKey(
        AddressClassifier,
        on_delete=models.DO_NOTHING,
        verbose_name="Населенный пункт",
        related_name="localities",
        blank=True,
        null=True,
    )
    district = models.ForeignKey(
        AddressClassifier,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Район",
        related_name="districts",
    )
    street = models.CharField(
        max_length=500,
        verbose_name="Улица",
        blank=True,
        null=True,
    )
    home_number = models.CharField(
        max_length=500,
        verbose_name="Дом",
        blank=True,
        null=True,
    )
    corpus = models.CharField(
        max_length=500,
        verbose_name="Корпус",
        blank=True,
        null=True
    )
    apartment = models.CharField(
        max_length=500,
        verbose_name="Квартира",
        blank=True,
        null=True
    )
    index = models.CharField(
        max_length=100,
        verbose_name="Индекс",
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        if not self.name:
            if self.region:
                self.name_en = f"{self.region} region, "
                self.name_ru = f"область {self.region}, "
                self.name_kk = f"{self.region} облысы, "
            if self.city:
                self.name_en = f"{self.city} city, "
                self.name_ru = f"г.{self.city}, "
                self.name_kk = f"{self.city} қ., "
            if self.street:
                self.name_en = f"St. {self.street}, "
                self.name_ru = f"ул. {self.street}, "
                self.name_kk = f"{self.street} к., "
            if self.home_number:
                self.name_en = f"#{self.home_number}, "
                self.name_ru = f"д. №{self.home_number}, "
                self.name_kk = f"№{self.home_number} үй, "
            if self.corpus:
                self.name_en += f", building {self.corpus}"
                self.name_ru += f", корпус {self.corpus}"
                self.name_kk += f", {self.corpus} ғимарат"
            if self.apartment:
                self.name_en += f", apartment {self.apartment}"
                self.name_ru += f", квартира {self.apartment}"
                self.name_kk += f", {self.apartment} пәтер"
            self.name = self.name_ru
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"


# Состав семьи
class Family(BaseModel):
    number_of_children = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Кол-во детей в семье"
    )
    number_of_young_children = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Кол-во несовершеннолетних детей в семье"
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Семья"
        verbose_name_plural = "Семьи"


# Член семьи
class FamilyMember(BaseModel):
    MATCH_REG = 0
    MATCH_TMP = 1
    MATCH_RES = 2
    MATCH_NOT = 3
    ADDRESS_MATCH_CHOICES = (
        (MATCH_REG, _('registration')),
        (MATCH_TMP, _('temporary registration')),
        (MATCH_RES, _('residence')),
        (MATCH_NOT, _('does not match'))
    )

    address_matches = models.CharField(
        max_length=1,
        choices=ADDRESS_MATCH_CHOICES,
        blank=True,
        null=True,
        verbose_name='Адрес соответствует'
    )
    first_name = models.CharField(
        max_length=255,
        default="",
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=255,
        default="",
        verbose_name="Фамилия"
    )
    middle_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Отчество"
    )
    family = models.ForeignKey(
        Family,
        blank=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Семья",
        related_name="members",
    )
    membership = models.ForeignKey(
        FamilyMembership,
        on_delete=models.DO_NOTHING,
        verbose_name="Степень родства"
    )
    profile = models.ForeignKey(
        Profile,
        blank=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Профиль"
    )
    workplace = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Место работы"
    )
    position = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Должность"
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.DO_NOTHING,
        verbose_name="Адрес"
    )
    phone = models.CharField(
        max_length=500,
        verbose_name="Телефон"
    )
    email = models.EmailField(
        max_length=500,
        verbose_name="Email"
    )

    class Meta:
        verbose_name = "Член семьи"
        verbose_name_plural = "Члены семьи"


class AdmissionCampaignType(BaseCatalog):
    prep_levels = models.ManyToManyField(PreparationLevel, verbose_name='Уровни образования')

    class Meta:
        verbose_name = 'Тип приемной кампании'
        verbose_name_plural = 'Типы приемных кампаний'


# Приемная кампания
class AdmissionCampaign(BaseCatalog):
    type = models.ForeignKey(
        AdmissionCampaignType,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)
    education_type = models.ForeignKey(
        EducationType,
        on_delete=models.DO_NOTHING,
        verbose_name="Тип образования"
    )
    use_contest_groups = models.BooleanField(
        default=False,
        verbose_name="Использовать конкурсные группы"
    )
    inter_cert_foreign_lang = models.BooleanField(
        default=False,
        verbose_name="Международный сертификат по иностранному языку"
    )
    chosen_directions_max_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Максимальное кол-во выбранных направлений"
    )
    year = models.CharField(
        max_length=4,
        verbose_name="Год поступления"
    )
    start_date = models.DateField("Дата начала приемной кампании")
    end_date = models.DateField("Дата окончания приемной кампании")

    def __str__(self):
        return f"{self.uid}"

    class Meta:
        verbose_name = "Приемная кампания"
        verbose_name_plural = "Приемные кампании"

    @property
    def info(self):
        return {
            # cdmc - максимум направлений, которые может выбрать абитуриент в этой кампании
            'cdmc': self.chosen_directions_max_count,
            # icfl - кампания принимает международные сертификаты
            'icfl': self.inter_cert_foreign_lang
        }


# Абитуриент
class Applicant(BaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.DO_NOTHING,
        related_name="applicant",
        blank=True,
        null=True,
        verbose_name="Пользователь"
    )
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=100,
    )
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=100,
    )
    middle_name = models.CharField(
        verbose_name="Отчество",
        max_length=100,
        blank=True,
        null=True
    )
    password = models.CharField(
        verbose_name="Пароль",
        max_length=100
    )
    confirm_password = models.CharField(
        verbose_name="Подтверждение пароля",
        max_length=100
    )
    email = models.EmailField(
        "Email",
        max_length=100,
        unique=True
    )
    doc_num = models.CharField(
        verbose_name="Серийный номер документа",
        max_length=16,
        unique=True
    )
    consented = models.BooleanField(
        verbose_name="Даю согласие на обработку моих персональных данных",
        default=False,
    )
    prep_level = models.ForeignKey(
        PreparationLevel,
        on_delete=models.DO_NOTHING,
        verbose_name="Уровень подготовки"
    )
    order_number = models.IntegerField(
        verbose_name="Порядковый номер",
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999)
        ],
    )
    campaign = models.ForeignKey(
        AdmissionCampaign,
        on_delete=models.SET_NULL,
        related_name='applicants',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Абитуриент"
        verbose_name_plural = "Абитуриенты"

    def generate_login(self, order_num):
        import time
        username = f"{self.prep_level.shifr[:2]}{time.strftime('%y')}{str(order_num).zfill(4)}"
        return username


# Сканы документов
class DocScan(models.Model):
    file = models.FileField(
        verbose_name="Файл",
        upload_to="media"
    )
    path = models.TextField(
        blank=True,
        null=True,
        verbose_name="Путь к файлу"
    )
    ext = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Расширение файла"
    )
    name = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Имя файла"
    )
    size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Размер файла"
    )
    # File"s content type not Django"s
    content_type = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Тип контента"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        null=True
    )

    def __str__(self):
        if self.name:
            return self.name
        else:
            return super().__str__()

    @staticmethod
    # Запись в media
    def handle_uploaded_file(f):
        from django.conf import settings
        with open(f"{settings.MEDIA_ROOT}/{f.name}", "wb+") as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    class Meta:
        verbose_name = "Скан документа"
        verbose_name_plural = "Сканы документов"


# Статус заявки
class ApplicationStatus(BaseCatalog):
    code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Код статуса",
    )

    @staticmethod
    def create_or_update():
        statuses = [
            {
                "name": APPROVED,
                "name_ru": "Заявление утверждено",
                "name_kk": "Өтініш бекітілді",
                "name_en": "Application approved",
                "code": APPROVED,
            },
            {
                "name": REJECTED,
                "name_ru": "Заявление отклонено",
                "name_kk": "Өтініш қабылданбады",
                "name_en": "Application rejected",
                "code": REJECTED,
            },
            {
                "name": AWAITS_VERIFICATION,
                "name_ru": "Ожидает проверки",
                "name_kk": "Тексеруді күтеді",
                "name_en": "Awaits verification",
                "code": AWAITS_VERIFICATION,
            },
            {
                "name": NO_QUESTIONNAIRE,
                "name_ru": "Без анкеты",
                "name_kk": "Сауалнамасыз",
                "name_en": "No questionnaire",
                "code": NO_QUESTIONNAIRE,
            },
        ]
        for status in statuses:
            match: [ApplicationStatus] = ApplicationStatus.objects.filter(code=status["code"])
            if match.exists():
                match.update(**status)
            else:
                ApplicationStatus.objects.create(**status)

    class Meta:
        verbose_name = "Статус заявления"
        verbose_name_plural = "Статусы заявлений"


# Анкета поступающего
class Questionnaire(BaseModel):
    MATCH_REG = 0
    MATCH_TMP = 1
    ADDRESS_MATCH_CHOICES = (
        (MATCH_REG, _('registration address')),
        (MATCH_TMP, _('temporary registration address')),
    )
    creator = models.OneToOneField(
        Profile,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Подающий анкету",
    )
    first_name = models.CharField(
        "Имя",
        max_length=255,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=255,
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        "Отчество",
        max_length=255,
        blank=True,
        null=True,
    )
    first_name_en = models.CharField(
        "Имя на латинице",
        max_length=255,
        blank=True,
        null=True,
    )
    last_name_en = models.CharField(
        "Фамилия на латинице",
        max_length=255,
        blank=True,
        null=True,
    )
    gender = models.ForeignKey(
        Gender,
        on_delete=models.DO_NOTHING,
        verbose_name="Пол"
    )
    marital_status = models.ForeignKey(
        MaritalStatus,
        on_delete=models.DO_NOTHING,
        verbose_name="Семейное положение",
        blank=True,
        null=True,
    )
    citizenship = models.ForeignKey(
        Citizenship,
        on_delete=models.DO_NOTHING,
        verbose_name="Гражданство"
    )
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.DO_NOTHING,
        verbose_name="Национальность"
    )
    is_experienced = models.BooleanField(
        default=False,
        verbose_name='Имеет опыт работы'
    )
    workplace = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Место работы"
    )
    position = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Должность"
    )
    experience_years = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Опыт в годах"
    )
    experience_months = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name="Опыт в месяцах",
        validators=[MinValueValidator(0), MaxValueValidator(12)],
    )
    birthday = models.DateField(
        verbose_name="День рождения"
    )
    birthplace = models.CharField(
        max_length=500,
        verbose_name="Место рождения"
    )
    id_doc = models.ForeignKey(
        IdentityDocument,
        on_delete=models.DO_NOTHING,
        verbose_name="Удостоверение личности",
    )
    iin = models.CharField(
        max_length=12,
        null=True,
        verbose_name='ИИН'
    )
    id_doc_scan = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name="Удо скан",
        related_name="application_id_doc",
    )
    phone = models.ForeignKey(
        ProfilePhone,
        on_delete=models.DO_NOTHING,
        verbose_name="Телефон",
        related_name="phones",
    )
    email = models.EmailField(
        max_length=100,
        verbose_name="Email"
    )
    address_of_registration = models.OneToOneField(
        Address,
        on_delete=models.DO_NOTHING,
        verbose_name="Адрес по прописке",
        related_name="registration_addresses",
    )
    address_of_residence = models.OneToOneField(
        Address,
        on_delete=models.DO_NOTHING,
        verbose_name="Адрес проживания",
        related_name="residence_addresses",
    )
    address_of_temp_reg = models.OneToOneField(
        Address,
        on_delete=models.DO_NOTHING,
        verbose_name="Адрес временной регистрации",
        blank=True,
        null=True,
        related_name="temporary_addresses",
    )
    family = models.OneToOneField(
        Family,
        on_delete=models.DO_NOTHING,
        verbose_name="Семья",
        related_name="questionnaires",
    )
    need_dormitory = models.BooleanField(
        default=False,
        verbose_name="Нуждается в общежитии"
    )
    doc_return_method = models.ForeignKey(
        DocumentReturnMethod,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Метод возврата документов",
    )
    address_matches = models.CharField(
        max_length=1,
        choices=ADDRESS_MATCH_CHOICES,
        verbose_name='Адресу фактического проживания соответствует',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Анкета"
        verbose_name_plural = "Анкеты"

    def __str__(self):
        if self.creator and self.creator.full_name:
            return f"Абитуриент {self.creator}"
        else:
            return f"Абитуриент {self.first_name_en} {self.last_name_en}"


# Список льгот пользователей
class UserPrivilegeList(BaseModel):
    questionnaire = models.OneToOneField(
        Questionnaire,
        on_delete=models.DO_NOTHING,
        verbose_name="Анкета",
        blank=True,
        null=True,
        related_name='privilege_list'
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Список льгот пользователя"
        verbose_name_plural = "Списки льгот пользователей"


# Льготы пользователей
class Privilege(BaseModel):
    type = models.ForeignKey(
        PrivilegeType,
        on_delete=models.DO_NOTHING,
        verbose_name="Тип льготы",
    )
    doc_type = models.ForeignKey(
        DocumentType,
        on_delete=models.DO_NOTHING,
        verbose_name="Тип документа"
    )
    serial_number = models.CharField(
        max_length=100,
        verbose_name="Серийный номер"
    )
    doc_number = models.CharField(
        max_length=100,
        verbose_name="Номер документа"
    )
    start_date = models.DateField(
        verbose_name="Дата начала"
    )
    end_date = models.DateField(
        verbose_name="Дата окончания"
    )
    issued_at = models.DateField(
        verbose_name="Дата получения"
    )
    issued_by = models.CharField(
        max_length=200,
        verbose_name="Кем выдано"
    )
    scan = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name="Скан документа"
    )
    list = models.ForeignKey(
        UserPrivilegeList,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Список льгот",
        related_name="privileges"
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Льгота"
        verbose_name_plural = "Льготы"


# Этапы приемной кампании
class CampaignStage(BaseModel):
    campaign = models.ForeignKey(
        AdmissionCampaign,
        on_delete=models.DO_NOTHING,
        related_name="stages",
        verbose_name="Приемная кампания"
    )
    prep_level = models.ForeignKey(
        PreparationLevel,
        on_delete=models.DO_NOTHING,
        related_name="campaign_stages",
        verbose_name="Уровень образования"
    )
    study_form = models.ForeignKey(
        StudyForm,
        on_delete=models.DO_NOTHING,
        verbose_name="Форма обучения",
    )
    education_base = models.ForeignKey(
        EducationBase,
        on_delete=models.DO_NOTHING,
        verbose_name="Основа поступления"
    )
    start_date = models.DateField(
        verbose_name="Дата начала"
    )
    end_date = models.DateTimeField(
        verbose_name="Дата окончания"
    )

    class Meta:
        verbose_name = "Этап кампании"
        verbose_name_plural = "Этапы кампаний"


# План набора
class RecruitmentPlan(BaseModel):
    campaign = models.ForeignKey(
        AdmissionCampaign,
        on_delete=models.DO_NOTHING,
        related_name="plans",
        verbose_name="План набора"
    )
    study_plan_1c = models.CharField(
        max_length=500,
        verbose_name="Учебный план из 1С"
    )
    prep_level = models.ForeignKey(
        PreparationLevel,
        on_delete=models.DO_NOTHING,
        related_name="plans",
        verbose_name="Уровень образования"
    )
    prep_direction = models.ForeignKey(
        Speciality,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Направление подготовки"
    )
    education_program = models.ForeignKey(
        EducationProgram,
        on_delete=models.DO_NOTHING,
        verbose_name="Образовательная программа"
    )
    education_program_group = models.ForeignKey(
        EducationProgramGroup,
        on_delete=models.DO_NOTHING,
        verbose_name="Группа образовательных программ"
    )
    graduating_cathedra = models.ForeignKey(
        Cathedra,
        on_delete=models.DO_NOTHING,
        verbose_name="Выпускающая кафедра"
    )
    study_form = models.ForeignKey(
        StudyForm,
        on_delete=models.DO_NOTHING,
        verbose_name="Форма обучения"
    )
    study_period = models.ForeignKey(
        StudyPeriod,
        on_delete=models.DO_NOTHING,
        verbose_name="Учебный период"
    )
    based_on = models.ForeignKey(
        EducationType,
        on_delete=models.DO_NOTHING,
        verbose_name="На базе"
    )
    admission_basis = models.ForeignKey(
        EducationBase,
        on_delete=models.DO_NOTHING,
        verbose_name="Основание для посутпления"
    )
    budget_level = models.ForeignKey(
        BudgetLevel,
        on_delete=models.DO_NOTHING,
        verbose_name="Уровень бюджета"
    )
    entrance_test_form = models.ForeignKey(
        ControlForm,
        on_delete=models.DO_NOTHING,
        verbose_name="Форма вступительного испытания"
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Язык обучения'
    )

    class Meta:
        verbose_name = "План набора"
        verbose_name_plural = "Планы наборов"


# Пройденная дисциплина с отметкой
class DisciplineMark(BaseModel):
    discipline = models.ForeignKey(
        Discipline,
        on_delete=models.DO_NOTHING,
        verbose_name="Дисциплина"
    )
    mark = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(40)]
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='my_disciplines'
    )

    class Meta:
        verbose_name = "Пройденная дисциплина на ЕНТ/КТ"
        verbose_name_plural = "Пройденные дисциплины на ЕНТ/КТ"


# Сертификат теста по ЕНТ/КТ
class TestCert(BaseModel):
    number = models.CharField(
        max_length=200,
        verbose_name="Номер сертификата"
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.DO_NOTHING,
        verbose_name="Язык сдачи",
    )
    issued_at = models.DateField(
        verbose_name="Дата сдачи экзамена"
    )
    confirmation_document_provided = models.BooleanField(
        default=False,
        verbose_name="Подтверждающий документ предоставлен"
    )
    scan = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name="Скан сертификата"
    )
    profile = models.ForeignKey(
        Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Профиль пользователя",
        related_name='my_test_certs'
    )

    class Meta:
        verbose_name = "Серитификат ЕНТ/КТ"
        verbose_name_plural = "Серитификаты ЕНТ/КТ"


# Навык владения языком
class LanguageProficiency(BaseModel):
    code = models.CharField(
        max_length=100,
        verbose_name="Код"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        related_name="children",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Уровень владения языком"
        verbose_name_plural = "Уровени владения языками"


# Международный сертификат
class InternationalCert(BaseModel):
    profile = models.ForeignKey(
        Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Профиль"
    )
    type = models.ForeignKey(
        InternationalCertType,
        on_delete=models.DO_NOTHING,
        verbose_name="Тип международного сертификата"
    )
    language_proficiency = models.ForeignKey(
        LanguageProficiency,
        on_delete=models.DO_NOTHING,
        verbose_name="Владение языком (CERF)"
    )
    mark = models.FloatField(
        verbose_name="Балл"
    )
    issued_at = models.DateField(
        verbose_name="Дата получения"
    )
    number = models.CharField(
        max_length=100,
        verbose_name="Номер сертификата"
    )

    class Meta:
        verbose_name = "Международный сертификат"
        verbose_name_plural = "Международные сертификаты"


# Грант
class Grant(BaseModel):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='grants',
        verbose_name='Профиль',
        blank=True,
        null=True
    )
    type = models.ForeignKey(
        GrantType,
        on_delete=models.DO_NOTHING,
        verbose_name="Вид гранта"
    )
    start_date = models.DateField(
        verbose_name="Дата начала"
    )
    end_date = models.DateField(
        verbose_name="Дата окончания"
    )
    issued_at = models.DateField(
        verbose_name="Дата выдачи"
    )
    serial_number = models.CharField(
        max_length=200,
        verbose_name="Серийный номер"
    )
    number = models.CharField(
        max_length=200,
        verbose_name="Номер"
    )
    date_of_order = models.DateField(
        verbose_name="Дата приказа МОН РК"
    )
    number_order = models.CharField(
        max_length=200,
        verbose_name="Номер приказа МОН РК"
    )
    speciality = models.ForeignKey(
        Speciality,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа образовательных программ'
    )
    scan = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name='Скан'
    )

    class Meta:
        verbose_name = "Грант"
        verbose_name_plural = "Грант"


# выбор направления
class DirectionChoice(BaseModel):
    prep_level = models.ForeignKey(
        PreparationLevel,
        on_delete=models.DO_NOTHING,
        verbose_name='Уровень образования'
    )
    study_form = models.ForeignKey(
        StudyForm,
        on_delete=models.DO_NOTHING,
        verbose_name='Форма обучения'
    )
    education_program = models.ForeignKey(
        EducationProgram,
        on_delete=models.DO_NOTHING,
        verbose_name='Образовательная программа'
    )
    education_program_group = models.ForeignKey(
        EducationProgramGroup,
        on_delete=models.DO_NOTHING,
        verbose_name='Группа образовательных программ'
    )
    education_base = models.ForeignKey(
        EducationBase,
        on_delete=models.DO_NOTHING,
        verbose_name='Основание поступления'
    )
    education_language = models.ForeignKey(
        Language,
        on_delete=models.DO_NOTHING,
        verbose_name='Язык обучения'
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='directions'
    )

    class Meta:
        verbose_name = "Выбор направления"
        verbose_name_plural = "Выборы направлений"


# Результат теста
class TestResult(BaseModel):
    disciplines = models.ManyToManyField(
        DisciplineMark,
        verbose_name='Пройденные дисциплины'
    )
    test_certificate = models.ForeignKey(
        TestCert,
        on_delete=models.DO_NOTHING,
        verbose_name='Сертификат теста'
    )
    profile = models.ForeignKey(
        Profile,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Результат ЕНТ/КТ"
        verbose_name_plural = "Результаты ЕНТ/КТ"


# Документы поступающего
class AdmissionDocument(BaseModel):
    recruitment_plan = models.ForeignKey(
        RecruitmentPlan,
        on_delete=models.SET_NULL,
        verbose_name='План набора',
        blank=True,
        null=True,
    )
    creator = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name='Профиль',
        blank=True,
        null=True,
    )
    files = models.ManyToManyField(
        DocScan,
        verbose_name='Сканы документов'
    )

    class Meta:
        verbose_name = 'Перечень документов для приема на обучение'
        verbose_name_plural = 'Перечни документов для приема на обучение'


# Заявление
class Application(BaseModel):
    previous_education = models.ForeignKey(
        Education,
        on_delete=models.DO_NOTHING,
        verbose_name='Предыдущее образование'
    )
    test_result = models.ForeignKey(
        TestResult,
        on_delete=models.DO_NOTHING,
        verbose_name='Результат теста ЕНТ/КТ'
    )
    international_cert = models.ForeignKey(
        InternationalCert,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Международный сертификат'
    )
    grant = models.ForeignKey(
        Grant,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name='Грант'
    )
    directions = models.ManyToManyField(
        DirectionChoice,
        verbose_name='Выборы направлений'
    )
    status = models.ForeignKey(
        ApplicationStatus,
        on_delete=models.DO_NOTHING,
        verbose_name='Статус',
        blank=True,
        null=True
    )
    creator = models.OneToOneField(
        Profile,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Заявитель',
    )
    questionnaire = models.OneToOneField(
        Questionnaire,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    admission_document = models.ForeignKey(
        AdmissionDocument,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Заявление"
        verbose_name_plural = "Заявления"

    def __str__(self):
        return f'Абитуриент {self.applicant}. {self.status.name}'

    @property
    def max_choices(self):
        campaign: AdmissionCampaign = self.creator.user.applicant.campaign
        return campaign.chosen_directions_max_count

    def import_self_to_1c(self):
        pass

    def approve(self, moderator, comment=None):
        if comment:
            Comment.objects.create(
                text=comment,
                creator=moderator,
                content_object=self
            )
        self.status = ApplicationStatus.objects.get(code=APPROVED)
        self.save()
        # TODO на подтверждение заявления модератором импортировать заявление в 1С
        self.import_self_to_1c()
        try:
            send_mail(
                subject='Ваше заявление подтверждено',
                message='Ваше заявление подтверждено модератором университета',
                from_email='',
                recipient_list=[self.creator.email]
            )
        except Exception as e:
            print(e)
        role: Role = Role.objects.get(profile=self.creator)
        role.is_applicant = False
        role.is_student = True
        role.save()
        return

    def reject(self, moderator, comment):
        Comment.objects.create(
            text=comment,
            creator=moderator,
            content_object=self
        )
        self.status = ApplicationStatus.objects.get(code=REJECTED)
        self.save()
        try:
            message = render_to_string('applicant/email/html/application_rejected.html', {
                'rejected_at': dt.datetime.now().strftime('%d.%m.%Y %H:%I'),
                'reason': comment
            })
            subject = 'Ваше заявление отклонено'
            email = EmailMessage(subject=subject, body=message, to=[self.creator.email])
            email.send()
        except Exception as e:
            print(e)
        return

    @property
    def status_info(self):
        return {
            'name': self.status.name,
            'code': self.status.code,
        }

    @property
    def applicant(self):
        return self.creator.full_name

    def delete(self, *args, **kwargs):
        previous_education = self.previous_education
        test_result = self.test_result
        international_cert = self.international_cert
        grant = self.grant
        directions = self.directions.all()
        super().delete(*args, **kwargs)
        if previous_education:
            previous_education.delete()
        if test_result:
            if test_result.disciplines.exists():
                [discipline.delete() for discipline in test_result.disciplines.all()]
            test_result.delete()
            test_result.test_certificate.delete()
        if international_cert:
            international_cert.delete()
        if grant:
            grant.delete()
        if directions.exists():
            [direction.delete() for direction in directions.all()]

    @staticmethod
    def can_perform_action(profile: Profile):
        if profile.role.is_mod:
            return True
        else:
            return False
