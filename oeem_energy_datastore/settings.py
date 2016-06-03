from __future__ import absolute_import

import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = os.environ.get("DEBUG","false").lower() == "true"

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'oauth2_provider',
    'rest_framework',
    'rest_framework_swagger',
    'api_doc',
    'datastore',
    'djcelery',
    'portal',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

if DEBUG:
    MIDDLEWARE_CLASSES += ('django_pdb.middleware.PdbMiddleware',)

ROOT_URLCONF = 'oeem_energy_datastore.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.core.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'oeem_energy_datastore.wsgi.application'

DATABASES = {'default': dj_database_url.config()}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get("STATIC_ROOT")

STATICFILES_DIRS = ( os.path.join(BASE_DIR,'staticfiles'),)

OAUTH2_PROVIDER = {
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope'},
    'ACCESS_TOKEN_EXPIRE_SECONDS': 315360000, # 10 years
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.ext.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

GRAPPELLI_ADMIN_TITLE = "Open Energy Efficiency Meter"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'DEBUG',
            'filters': ['require_debug_false'],
            'class': 'logging.handlers.WatchedFileHandler',
            'formatter': 'verbose',
            'filename': os.environ.get("DJANGO_LOGFILE", "django.log"),
        },
        'celery': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.environ.get("CELERY_LOGFILE", "celery.log"),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
        'celery': {
            'handlers': ['console', 'celery'],
            'level': 'DEBUG',
        },
    },
}

BROKER_URL = os.environ.get("BROKER_URL", None)

# defaults for development, should be overriden in production.
BROKER_TRANSPORT = os.environ.get("BROKER_TRANSPORT", "memory")
CELERY_ALWAYS_EAGER = os.environ.get("CELERY_ALWAYS_EAGER", "true").lower() == "true"

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

SWAGGER_SETTINGS = {
    'base_path': '{}/docs'.format(os.environ["SERVER_NAME"]),
    'protocol': os.environ["PROTOCOL"],
}


# DJANGO DEBUG TOOLBAR
if DEBUG:
    INSTALLED_APPS += ('debug_toolbar',)
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    DEBUG_TOOLBAR_PATCH_SETTINGS = False
    INTERNAL_IPS = ['0.0.0.0', '127.0.0.1', 'localhost']

