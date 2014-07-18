"""
Django settings for pm project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'qy!*%gmw&-cplyk0d7m)x-l@+7=^%d+ogv(*dshb!29!re@u!t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost',]


# Application definition

DEFAULT_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    'south',
    'piston',
    'rest_framework',
    'rest_framework.authtoken',
    'sslserver',
)

MY_APPS = (
    'projects',
    'api',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + MY_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pm.urls'

WSGI_APPLICATION = 'pm.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# Production: change database name to '/var/www/vhosts/wpeopm.wpengine.com/wpeopm/db/db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db/db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
# Development
STATIC_ROOT = '/home/matthew/pm/static/'
# Production
#STATIC_ROOT = '/var/www/vhosts/wpeopm.wpengine.com/static/'

# Template directories

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

# Login and logout URLs for django.contrib.auth

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/projects/'

# Media upload path and URL

MEDIA_ROOT = '/home/matthew/pm/uploads/'
MEDIA_URL = 'http://localhost:8000/files/'

# API settings
REST_FRAMEWORK = {
    # Use hyperlinked styles by default
    # Only used if the 'serializer_class' attribute is not set on a view
#    'DEFAULT_MODEL_SERIALIZER_CLASS': 'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard 'django.contrib.auth' permissions,
    # or allow read-only access for unauthenticated users.
#    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
#    'PAGINATE_BY': 10
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

HTTPS_SUPPORT = True

#### Nothing should go below this line!!

# Local setting overrides are stored in local_settings.py and are specific to the environment
# local_settings.py is not under version control

try:
    from local_settings import *
except ImportError, e:
    pass
