"""
Django settings for trivia_stats project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import json

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*$z&ycknu0k(l5w#=u7#mr769c+$8l(gz2=@rx9=!^r+r7w(61'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'corsheaders',
    'website'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

APPEND_SLASH = False

ROOT_URLCONF = 'trivia_stats.urls'

WSGI_APPLICATION = 'trivia_stats.wsgi.application'

CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
    'www.trivastats.com'
)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DEFAULT_DATABASE = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '192.168.2.2',
        'NAME': 'triviastats',
        'USER': 'root',
        'PASSWORD': 'password'
    }
}

DATABASES = os.environ.get('DJANGO_DATABASE', DEFAULT_DATABASE)

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination'
}

DJOSER = {
    'DOMAIN': 'triviastats.com',
    'SITE_NAME': 'TriviaStats',
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'LOGIN_AFTER_ACTIVATION': True,
    'LOGIN_AFTER_REGISTRATION': True,
    'SEND_ACTIVATION_EMAIL': False,
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "trivia_stats/static"),
)

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Serve the frontend files while developing
if DEBUG:
    STATICFILES_DIRS += ('frontend',)

QUERY_INSPECT_ENABLED = True
QUERY_INSPECT_LOG_STATS = True
QUERY_INSPECT_LOG_QUERIES = True
QUERY_INSPECT_ABSOLUTE_LIMIT = 100  # in milliseconds
QUERY_INSPECT_STANDARD_DEVIATION_LIMIT = 2
QUERY_INSPECT_LOG_TRACEBACKS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] "
                      "%(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "logs",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'logfile'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'qinspect': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
FROM_EMAIL = 'triviastats@triviastats.com'
TWILIO_NUMBER = '+17154464491'

# Whether to send notifications or not
DO_NOTIFICATIONS = False
DISABLE_TWITTER = False

try:
    from config.production_settings import *  # noqa
except ImportError:
    pass

# Load environment overrides
try:
    env = os.environ.get('DJANGO_ENV', '{}')
    for key, value in json.loads(env).items():
        print("Overring setting: {} to {}".format(key, value))
        vars()[key] = value
except ValueError:
    pass
