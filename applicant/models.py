from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import EmailMultiAlternatives
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Case, When, Value, Q
from django.template import Context
from django.template.loader import get_template
from common.models import (
    BaseModel,
    BaseCatalog,
    Comment,
    IdentityDocument,
    Citizenship,
    Nationality,
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
IMPROVE = "IMPROVE"

COND_ORDER = Case(
    When(Q(status__code=AWAITS_VERIFICATION), then=Value(0)),
    When(Q(status__code=NO_QUESTIONNAIRE), then=Value(1)),
    When(Q(status__code=IMPROVE), then=Value(3)),
    When(Q(status__code=APPROVED), then=Value(4)),
    When(Q(status__code=REJECTED), then=Value(5)),
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


# Тип адреса
class AddressType(BaseCatalog):

    class Meta:
        verbose_name = "Тип адреса"
        verbose_name_plural = "Типы адресов"


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
    address_element_type = models.PositiveSmallIntegerField(
        verbose_name="Тип адресного элемента"
    )
    district_code = models.PositiveSmallIntegerField(
        verbose_name="Код района",
        blank=True,
        null=True
    )
    region_code = models.PositiveSmallIntegerField(
        verbose_name="Код региона",
        blank=True,
        null=True
    )
    locality_code = models.PositiveSmallIntegerField(
        verbose_name="Код населенного пункта",
        blank=True,
        null=True  # Населенный пункт
    )
    code = models.PositiveSmallIntegerField(
        verbose_name="Код",
    )

    class Meta:
        verbose_name = "Адресный классификатор"
        verbose_name_plural = "Адресные классификаторы"


# Адрес пользователя
class Address(BaseCatalog):
    # Представление адреса будет потом после создания
    name = models.CharField(
        blank=True,
        null=True,
        max_length=800,
        verbose_name="Имя",
    )
    profile = models.ForeignKey(
        Profile,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Профиль",
        related_name="addresses",
    )
    type = models.ForeignKey(
        AddressType,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Тип адреса"
    )
    country = models.ForeignKey(
        Citizenship,
        on_delete=models.DO_NOTHING,
        verbose_name="Страна",
        related_name="addresses",
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
    city = models.ForeignKey(
        AddressClassifier,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Город",
        related_name="cities",
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
        verbose_name="Улица"
    )
    home_number = models.CharField(
        max_length=500,
        verbose_name="Дом"
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
        verbose_name="Индекс"
    )

    def save(self, *args, **kwargs):
        if not self.name:
            # В инглише однако порядок наоборот
            self.name_en = f"{self.region} region, {self.city}, st. {self.street}, house number {self.home_number}"
            self.name_ru = f"{self.region}, г. {self.city}, ул. {self.street}, дом №{self.home_number}"
            self.name_kk = (
                f"{self.region}, {self.city} қ. {self.street}, № {self.home_number} үй"
            )

            if self.corpus:
                self.name_en += f", building {self.corpus}"
                self.name_ru += f", корпус {self.corpus}"
                self.name_kk += f", {self.corpus} ғимарат"
            if self.apartment:
                self.name_en += f", apartment {self.apartment}"
                self.name_ru += f", квартира {self.apartment}"
                self.name_kk += f", {self.apartment} пәтер"
            self.name = self.name_kk
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

    class Meta:
        verbose_name = "Семья"
        verbose_name_plural = "Семьи"


# Член семьи
class FamilyMember(BaseModel):
    # Мне кажется, что в ТЗ не очень продуманно с составом семьи.
    # Например, заполнять кол-во детей и кол-во несовершеннолетних в семье
    # на каждого члена семьи не нужно и затратно по времени.
    # Лучше создать реальную модель семьи с ее членами и такую информацию о кол-ве детей
    # закинуть в саму семью и подвязать к абитуриенту
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

    @staticmethod
    def send_credentials(username, email, password):
        url = "qwerty/asd"
        context = Context({"username": username, "password": password, "url": url})
        plain_text = get_template("applicant/email/txt/send_credentials.txt").render(context.dicts[1])
        html = get_template("applicant/email/html/send_credentials.html").render(context.dicts[1])
        subject, email_from, to = (
            "Successfully registered",
            "alibekkaparov@gmail.com",
            [email],
        )
        message = EmailMultiAlternatives(subject, plain_text, email_from, to)
        message.attach_alternative(html, "text/html")
        result = message.send()
        return result

    class Meta:
        verbose_name = "Абитуриент"
        verbose_name_plural = "Абитуриенты"


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

    def __str__(self):
        if self.name:
            return self.name
        else:
            return super().__str__()

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
            {
                "name": IMPROVE,
                "name_ru": "Требует доработки",
                "name_kk": "Жақсартуды қажет етеді",
                "name_en": "Needs to be improved",
                "code": IMPROVE
            }
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
    creator = models.OneToOneField(
        Profile,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Подающий анкету",
    )
    first_name_en = models.CharField(
        "Имя на латинице",
        max_length=255,
    )
    last_name_en = models.CharField(
        "Фамилия на латинице",
        max_length=255,
    )
    gender = models.ForeignKey(
        Gender,
        on_delete=models.DO_NOTHING,
        verbose_name="Пол"
    )
    marital_status = models.ForeignKey(
        MaritalStatus,
        on_delete=models.DO_NOTHING,
        verbose_name="Семейное положение"
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
        verbose_name="Удо",
    )
    iin = models.CharField(
        max_length=12,
        null=True
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

    class Meta:
        verbose_name = "Анкета"
        verbose_name_plural = "Анкеты"


# Список льгот пользователей
class UserPrivilegeList(BaseModel):
    need_dormitory = models.BooleanField(
        default=False,
        verbose_name="Нуждаюсь в общежитии"
    )
    questionnaire = models.OneToOneField(
        Questionnaire,
        on_delete=models.DO_NOTHING,
        verbose_name="Анкета",
        null=True,
    )
    doc_return_method = models.ForeignKey(
        DocumentReturnMethod,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Метод возврата документов",
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
    comments = GenericRelation(Comment)
    questionnaire = models.OneToOneField(
        Questionnaire,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Заявление"
        verbose_name_plural = "Заявления"

    def import_self_to_1c(self):
        pass

    def approve(self, moderator, comment=None):
        if comment:
            self.comments.create(creator=moderator, text=comment)
        self.status = ApplicationStatus.objects.get(code=APPROVED)
        self.save()
        # TODO на подтверждение заявления модератором импортировать заявление в 1С
        role = Role.objects.get(profile=self.creator)
        role.is_applicant, role.is_student = role.is_student, role.is_applicant
        role.save()

    def reject(self, moderator, comment):
        self.comments.create(creator=moderator, text=comment)
        self.status = ApplicationStatus.objects.get(code=REJECTED)
        self.save()

    def improve(self, moderator, comment):
        self.comments.create(creator=moderator, text=comment)
        self.status = ApplicationStatus.objects.get(code=IMPROVE)
        self.save()

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


class AdmissionDocument(BaseModel):
    campaign = models.ForeignKey(
        AdmissionCampaign,
        on_delete=models.SET_NULL,
        verbose_name='Кампания',
        blank=True,
        null=True,
    )
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
        verbose_name='Профиль'
    )
    files = models.ManyToManyField(
        DocScan,
        verbose_name='Сканы документов'
    )

    class Meta:
        verbose_name = 'Перечень документов для приема на обучение'
        verbose_name_plural = 'Перечни документов для приема на обучение'


# История изменения заявления
class Changelog(BaseModel):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='changelog'
    )
    related_model_name = models.CharField(
        'Название модели, которая была изменена',
        max_length=300
    )
    key = models.CharField(
        'Ключ',
        max_length=300
    )
    old_value = models.CharField(
        'Старое значение',
        max_length=300,
        blank=True,
        default=''
    )
    new_value = models.CharField(
        'Новое значение',
        max_length=300,
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = 'Изменения заявления'
        verbose_name_plural = 'Изменения заявлений'

    def __str__(self):
        return f'Изменена модель {self.related_model_name}.'
