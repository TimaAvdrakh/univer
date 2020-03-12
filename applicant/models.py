from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from common.models import (
    BaseModel,
    BaseCatalog,
    IdentityDocument,
    Citizenship,
    Nationality,
)
from portal_users.models import Profile, ProfilePhone, Gender, MaritalStatus
from organizations.models import (
    PreparationLevel,
    Speciality,
    EducationProgram,
    StudyForm,
    StudyPeriod,
    EducationType,
    EducationBase,
    EducationProgramGroup,
    Cathedra,
    ControlForm,
)
from organizations.models import DocumentType


APPROVED = "APPROVED"
REJECTED = "REJECTED"
WAITING_VERIFY = "WAITING_VERIFY"
ALL = "ALL"
NO_STATEMENT = "NO_STATEMENT"


# Вид льготы
class PrivilegeType(BaseCatalog):

    class Meta:
        verbose_name = _("Privilege type")
        verbose_name_plural = _("Privilege types")


# Способ возврата документа
class DocumentReturnMethod(BaseCatalog):

    class Meta:
        verbose_name = _("Document return method")
        verbose_name_plural = _("Document return methods")


# Членство в семье
class FamilyMembership(BaseCatalog):

    class Meta:
        verbose_name = _("Family membership")
        verbose_name_plural = _("Family memberships")


# Тип адреса
class AddressType(BaseCatalog):

    class Meta:
        verbose_name = _("Address type")
        verbose_name_plural = _("Address types")


# Уровни бюджета
class BudgetLevel(BaseCatalog):

    class Meta:
        verbose_name = _("Budget level")
        verbose_name_plural = _("Budget levels")


# Адресный классификатор
class AddressClassifier(BaseCatalog):
    address_element_type = models.PositiveSmallIntegerField(
        verbose_name=_("Type of address element")
    )
    district_code = models.PositiveSmallIntegerField(
        verbose_name=_("District code"),
        blank=True,
        null=True
    )
    region_code = models.PositiveSmallIntegerField(
        verbose_name=_("Region code"),
        blank=True,
        null=True
    )
    locality_code = models.PositiveSmallIntegerField(
        verbose_name=_("Locality code"),
        blank=True,
        null=True  # Населенный пункт
    )
    code = models.PositiveSmallIntegerField(
        verbose_name=_("Code"),
    )


# Адрес пользователя
class Address(BaseModel):
    # Представление адреса будет потом после создания
    name = models.CharField(
        blank=True,
        null=True,
        max_length=800,
        verbose_name=_("Name"),
    )
    profile = models.ForeignKey(
        Profile,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Profile"),
        related_name="addresses",
    )
    type = models.ForeignKey(
        AddressType,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Address type")
    )
    country = models.ForeignKey(
        Citizenship,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Country"),
        related_name="addresses",
    )
    region = models.ForeignKey(
        AddressClassifier,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Region"),
        related_name="regions",
    )
    locality = models.ForeignKey(
        AddressClassifier,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Locality"),
        related_name="localities",
        blank=True,
        null=True,
    )
    city = models.ForeignKey(
        AddressClassifier,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("City"),
        related_name="cities",
    )
    district = models.ForeignKey(
        AddressClassifier,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("District"),
        related_name="districts",
    )
    street = models.CharField(
        max_length=500,
        verbose_name=_("Street")
    )
    home_number = models.CharField(
        max_length=500,
        verbose_name=_("Home")
    )
    corpus = models.CharField(
        max_length=500,
        verbose_name=_("Corpus"),
        blank=True,
        null=True
    )
    apartment = models.CharField(
        max_length=500,
        verbose_name=_("Apartment"),
        blank=True,
        null=True
    )
    index = models.CharField(
        max_length=100,
        verbose_name=_("Index")
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


# Состав семьи
class Family(BaseModel):
    number_of_children = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Number of children")
    )
    number_of_young_children = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Number of underage children")
    )


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
        verbose_name=_("First name")
    )
    last_name = models.CharField(
        max_length=255,
        default="",
        verbose_name=_("Last name")
    )
    middle_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Middle name")
    )
    family = models.ForeignKey(
        Family,
        blank=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Family"),
        related_name="members",
    )
    membership = models.ForeignKey(
        FamilyMembership,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Membership")
    )
    profile = models.ForeignKey(
        Profile,
        blank=True,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Profile")
    )
    workplace = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )
    position = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Position")
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Address of residence")
    )
    phone = models.CharField(
        max_length=500,
        verbose_name=_("Phone")
    )
    email = models.EmailField(
        max_length=500,
        verbose_name=_("Email")
    )

    class Meta:
        verbose_name = _("Family member")
        verbose_name_plural = _("Family members")


# Тип приемной кампании
class AdmissionCampaignType(BaseCatalog):
    """Тип приемной компании"""

    code = models.CharField(
        _("Admission campaign type code"), max_length=10, blank=True, null=True,
    )

    class Meta:
        verbose_name = _("Admission campaign type")
        verbose_name_plural = _("Admission campaign types")


# Приемная кампания
class AdmissionCampaign(BaseCatalog):
    """Кампания"""
    # campaign_type = models.ForeignKey(
    #     AdmissionCampaignType,
    #     on_delete=models.DO_NOTHING,
    #     verbose_name=_("Admission campaign type"),
    # )
    # prep_level = models.ForeignKey(
    #     PreparationLevel,
    #     on_delete=models.DO_NOTHING,
    #     verbose_name=_("Preparation level"),
    # )
    education_type = models.ForeignKey(
        EducationType,
        on_delete=models.DO_NOTHING,
        verbose_name=_("")
    )
    use_contest_groups = models.BooleanField(
        default=False,
        verbose_name=_("Use contest groups")
    )
    inter_cert_foreign_lang = models.BooleanField(
        default=False,
        verbose_name=_("International certificate foreign language")
    )
    chosen_directions_max_count = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Maximal count of applicant's chosen directions")
    )
    year = models.CharField(
        max_length=4,
        verbose_name=_("Year of admission")
    )
    start_date = models.DateField(_("Admission campaign starting date"))
    end_date = models.DateField(_("Admission campaign ending date"))

    def __str__(self):
        return f"{self.campaign_type.name} - {self.prep_level.shifr}"

    class Meta:
        verbose_name = _("Admission campaign")
        verbose_name_plural = _("Admission campaigns")


# Абитуриент
class Applicant(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="applicant",
        blank=True,
        null=True,
    )
    first_name = models.CharField(
        _("First name"),
        max_length=100,
    )
    last_name = models.CharField(
        _("Last name"),
        max_length=100,
    )
    middle_name = models.CharField(
        _("Middle name"),
        max_length=100,
        blank=True,
        null=True
    )
    password = models.CharField(
        _("Password"),
        max_length=100
    )
    confirm_password = models.CharField(
        _("Password confirmation"),
        max_length=100
    )
    email = models.EmailField(
        _("Email"),
        max_length=100,
    )
    doc_num = models.CharField(
        _("Identification document serial number"),
        max_length=16,
        unique=True
    )
    consented = models.BooleanField(
        _("Consent given to process personal data"),
        default=False,
    )
    prep_level = models.ForeignKey(
        PreparationLevel,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Preparation level")
    )
    order_number = models.IntegerField(
        _("Order number"),
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(9999)
        ],
    )

    class Meta:
        verbose_name = _("Applicant")
        verbose_name_plural = _("Applicants")

    def generate_login(self, order_num):
        import time
        username = f"{self.prep_level.shifr[:2]}{time.strftime('%y')}{str(order_num).zfill(4)}"
        return username

    @staticmethod
    def verify_email():
        subject = "Account activation"
        message = None
        pass

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


# Сканы документов
class DocScan(models.Model):
    file = models.FileField(
        verbose_name=_("File"),
        upload_to="media"
    )
    path = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Path to file")
    )
    ext = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("File extension")
    )
    name = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("File name")
    )
    size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("File size")
    )
    # File's content type not Django's
    content_type = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Content type of a file")
    )

    def __str__(self):
        if self.name:
            return self.name
        else:
            return super().__str__()

    class Meta:
        verbose_name = _("Scan of document")
        verbose_name_plural = _("Scans of documents")


# Статус заявки
class ApplicationStatus(BaseCatalog):
    code = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Code of application status"),
    )

    @staticmethod
    def create_or_update():
        statuses = [
            {
                "name": "Approved",
                "name_ru": "Утверждена",
                "name_kk": "",
                "name_en": "Approved",
                "code": APPROVED,
            },
            {
                "name": "Rejected",
                "name_ru": "Отклонена",
                "name_kk": "",
                "name_en": "Rejected",
                "code": REJECTED,
            },
            {
                "name": "Awaits verification",
                "name_ru": "Ожидает проверки",
                "name_kk": "",
                "name_en": "Awaits verification",
                "code": WAITING_VERIFY,
            },
            {
                "name": "All",
                "name_ru": "Все",
                "name_kk": "",
                "name_en": "All",
                "code": ALL,
            },
            {
                "name": "No statement",
                "name_ru": "Без заявления",
                "name_kk": "",
                "name_en": "No statement",
                "code": NO_STATEMENT,
            },
        ]
        for status in statuses:
            if ApplicationStatus.objects.filter(code=status["code"]):
                ApplicationStatus.objects.filter(code=status["code"]).update(**status)
            else:
                ApplicationStatus.objects.create(**status)

    class Meta:
        verbose_name = _("Application status")
        verbose_name_plural = _("Application statuses")


# Анкета поступающего
class Questionnaire(BaseModel):
    applicant = models.ForeignKey(
        User,
        blank=True,
        on_delete=models.DO_NOTHING,
        related_name="questionnaires",
        verbose_name=_("Applicant"),
    )
    first_name_en = models.CharField(
        max_length=255,
        verbose_name=_("English first name")
    )
    last_name_en = models.CharField(
        max_length=255,
        verbose_name=_("English last name"))
    gender = models.ForeignKey(
        Gender,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Gender")
    )
    marital_status = models.ForeignKey(
        MaritalStatus,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Marital status")
    )
    citizenship = models.ForeignKey(
        Citizenship,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Citizenship")
    )
    nationality = models.ForeignKey(
        Nationality,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Nationality")
    )
    workplace = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Workplace")
    )
    position = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Position")
    )
    experience_years = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Experience in years")
    )
    experience_months = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Experience in months"),
        validators=[MinValueValidator(0), MaxValueValidator(12)],
    )
    birthday = models.DateField(
        verbose_name=_("Birthday")
    )
    birthplace = models.CharField(
        max_length=500,
        verbose_name=_("Birthplace")
    )
    id_doc = models.ForeignKey(
        IdentityDocument,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Identity document"),
    )
    id_doc_scan = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Identification document"),
        related_name="application_id_doc",
    )
    phone = models.ForeignKey(
        ProfilePhone,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Phone"),
        related_name="phones",
    )
    email = models.EmailField(
        max_length=100,
        verbose_name=_("Email")
    )
    address_of_registration = models.ForeignKey(
        Address,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Address of registration"),
        related_name="registration_addresses",
    )
    address_of_residence = models.ForeignKey(
        Address,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Address of residence"),
        related_name="residence_addresses",
    )
    address_of_temp_reg = models.ForeignKey(
        Address,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Temporary registration address"),
        blank=True,
        null=True,
        related_name="temporary_addresses",
    )
    family = models.ForeignKey(
        Family,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Family"),
        related_name="questionnaires",
    )

    class Meta:
        verbose_name = _("Questionnaire")
        verbose_name_plural = _("Questionnaires")


# Льготы пользователей
class Privilege(BaseModel):
    type = models.ForeignKey(
        PrivilegeType,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Type of privilege"),
    )
    doc_type = models.ForeignKey(
        DocumentType,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Type of document")
    )
    serial_number = models.CharField(
        max_length=100,
        verbose_name=_("Serial number"))
    doc_number = models.CharField(
        max_length=100,
        verbose_name=_("Document number"))
    start_date = models.DateField(
        verbose_name=_("Start date")
    )
    end_date = models.DateField(
        verbose_name=_("End date")
    )
    issued_at = models.DateField(
        verbose_name=_("Issued at")
    )
    issued_by = models.CharField(
        max_length=200,
        verbose_name=_("Issued by")
    )
    scan = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Document scan")
    )
    doc_return_method = models.ForeignKey(
        DocumentReturnMethod,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name=_("Document return method"),
    )
    need_dormitory = models.BooleanField(
        default=False, verbose_name=_("Need dormitory to live")
    )
    questionnaire = models.ForeignKey(
        Questionnaire,
        on_delete=models.DO_NOTHING,
        related_name="questionnaires",
        verbose_name=_("Questionnaire link"),
    )

    class Meta:
        verbose_name = _("Privilege")
        verbose_name_plural = _("Privileges")


# Заявка на поступление
class AdmissionApplication(BaseModel):
    form = models.ForeignKey(
        Questionnaire,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Applicant form"),
        related_name="applications",
    )
    academic_background = models.CharField(
        max_length=500,
        verbose_name=_("Academic background")
    )
    diploma_num = models.CharField(
        max_length=100,
        verbose_name=_("Diploma number"),
        unique=True
    )
    diploma_scan = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Diploma scan document"),
        related_name="application_diploma",
    )
    ent_results = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name=_("ENT results"),
        related_name="application",
    )
    grant_num = models.CharField(
        max_length=100,
        verbose_name=_("Grant number"),
        blank=True,
        null=True
    )
    grant_order_date = models.DateField(
        verbose_name=_("Order date of grant"),
        blank=True,
        null=True
    )
    grant_scan = models.ForeignKey(
        DocScan,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Grant scan"),
        blank=True,
        null=True,
        related_name="application_grant",
    )
    programs = models.ManyToManyField(
        EducationProgram,
        verbose_name=_("Programs")
    )
    speciality = models.ForeignKey(
        Speciality,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Speciality")
    )
    education_base = models.ForeignKey(
        EducationBase,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Education base")
    )
    extra_info = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Extra information about applicant, like interests and achievements"),
    )
    files = models.ManyToManyField(
        DocScan,
        blank=True,
        verbose_name=_("Extra attachments"),
        related_name="application_extra",
    )
    status = models.ForeignKey(
        ApplicationStatus,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Application status"),
        related_name="applications",
    )

    class Meta:
        verbose_name = _("Admission application")
        verbose_name_plural = _("Admission applications")

    def notify_applicant(self):
        pass


# Этапы приемной кампании
class CampaignStage(BaseModel):
    campaign = models.ForeignKey(
        AdmissionCampaign,
        on_delete=models.DO_NOTHING,
        related_name="stages",
        verbose_name=_("Admission campaign")
    )
    prep_level = models.ForeignKey(
        PreparationLevel,
        on_delete=models.DO_NOTHING,
        related_name="campaign_stages",
        verbose_name=_("Preparation level")
    )
    study_form = models.ForeignKey(
        StudyForm,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Study form"),
    )
    education_base = models.ForeignKey(
        EducationBase,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Education base")
    )
    start_date = models.DateField(
        _("The beginning date of document receipt")
    )
    end_date = models.DateTimeField(
        _("The ending date of document receipt")
    )
    # admission_year = models.CharField(
    #     _("Year of admission to university"),
    #     max_length=4,
    # )
    # order_date = models.DateField(
    #     _("Date of order execution"),
    #     blank=True,
    #     null=True
    # )

    class Meta:
        verbose_name = _("Campaign stage")
        verbose_name_plural = _("Campaign stages")


# План набора
class RecruitmentPlan(BaseModel):
    campaign = models.ForeignKey(
        AdmissionCampaign,
        on_delete=models.DO_NOTHING,
        related_name="plans",
        verbose_name=_("Recruitment plan")
    )
    study_plan_1c = models.CharField(
        max_length=500,
        verbose_name=_("1C study plan")
    )
    prep_level = models.ForeignKey(
        PreparationLevel,
        on_delete=models.DO_NOTHING,
        related_name='plans',
        verbose_name=_("Preparation level")
    )
    training_direction = models.ForeignKey(
        Speciality,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Training direction")
    )
    education_program = models.ForeignKey(
        EducationProgram,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Education program")
    )
    education_program_group = models.ForeignKey(
        EducationProgramGroup,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Group of education programs")
    )
    graduating_cathedra = models.ForeignKey(
        Cathedra,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Graduating cathedra")
    )
    study_form = models.ForeignKey(
        StudyForm,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Study Form")
    )
    study_period = models.ForeignKey(
        StudyPeriod,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Study period")
    )
    based_on = models.ForeignKey(
        EducationType,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Based on")
    )
    admission_basis = models.ForeignKey(
        EducationBase,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Admission basis")
    )
    budget_level = models.ForeignKey(
        BudgetLevel,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Budget level")
    )
    entrance_test_form = models.ForeignKey(
        ControlForm,
        on_delete=models.DO_NOTHING,
        verbose_name=_("Entrance test form")
    )
