"""
Django settings for portal project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
from .local_settings import *

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'common',
    'portal_users',
    'rest_framework_swagger',
    'rest_framework_recaptcha',
    'corsheaders',
    'django_cron',
    'cron_app',
    'bootstrap4',
    'organizations',
    'modeltranslation',
    'advisors',
    'reports',
    'schedules',
    'c1',
    'univer_admin',
    'student_journal',
    'integration',
    'applicant'
]

MIDDLEWARE = [
    # Ало. В доке к corsheaders написано, что его мидлварь должна быть самая первая
    # я 1.5 часа искал ответ почему мои запросы не проходят
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'portal.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_L10N = True

USE_TZ = True

gettext = lambda s: s
LANGUAGES = (
    ('ru', gettext('Russian')),
    ('kk', gettext('Kazakh')),
    ('en', gettext('English')),
)

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'common.csrf_exempt_auth_class.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        # 'rest_framework.parsers.FileUploadParser',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    # 'DATE_INPUT_FORMATS': ['%d.%m.%Y'],
    # 'DATE_FORMAT': '%d.%m.%Y',
    # 'DATETIME_FORMAT': '%d.%m.%Y %H:%I:%S'
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CRON_CLASSES = [
    "cron_app.cron.EmailCronJob",
    "cron_app.cron.PasswordResetUrlSendJob",
    # "cron_app.cron.SendCredentialsJob",
    "cron_app.cron.NotifyAdvisorJob",
    "cron_app.cron.AdvisorRejectBidJob",
    "cron_app.cron.StudPerformanceChangedJob",
    "cron_app.cron.ControlNotifyJob",
    "cron_app.cron.CloseLessonsJob",
    # "cron_app.cron.SendStudentDisciplinesTo1CJob",
    # "cron_app.cron.SendConfirmedDisciplineCreditTo1CJob",
    # "cron_app.cron.SendConfirmedThemesOfTheses",
    "cron_app.cron.ClosePlannedJournalJob",
    "cron_app.cron.GenerateExcelJob",
    # "cron_app.cron.DeleteDuplicateJob",
]

# SESSION_COOKIE_AGE = 60

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
