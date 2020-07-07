from django.db import models
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
    Citizenship,
    Nationality,
    Changelog
)
from portal_users.models import (
    Profile,
    Gender,
    Role
)



# Create your models here.
