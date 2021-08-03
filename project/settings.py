"""
Django settings for this project.

Generated by 'django-admin startproject' using Django 2.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    # safe value used for development when DJANGO_SECRET_KEY might not be set
    '9e4@&tw46$l31)zrqe3wi+-slqm(ruvz&se0^%9#6(_w3ui!c0'
)


ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST')]
DEBUG = os.getenv('DEBUG', False)

ADMINS = [('Admins', 'srs-exception@umich.edu')]

# Application definition

INSTALLED_APPS = [
    'oscauth',
    'project',
    'django.forms', # try to override widgets
    'django.contrib.admin',
    'django.contrib.auth',
    'mozilla_django_oidc',  # Load after auth
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'django_extensions',
    'debug_toolbar',
    'order',
    'pages',
    'reports',
    'tools',
    'apps',
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAdminUser'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'  # Override widgets

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'oscauth.backends.UMichOIDCBackend',
    'django.contrib.auth.backends.ModelBackend',
    'oscauth.backends.SuBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# mozilla-django-oidc
ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEV')
SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')
OIDC_RP_CLIENT_ID = os.getenv('OIDC_RP_CLIENT_ID', 'N/A')
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET','N/A')
AUTH_BASE_URL = os.getenv('AUTH_BASE_URL','https://shib-idp-staging.dsc.umich.edu')
OIDC_CALLBACK = SITE_URL + '/oidc/callback/'
OIDC_OP_AUTHORIZATION_ENDPOINT = AUTH_BASE_URL + '/idp/profile/oidc/authorize'
OIDC_OP_TOKEN_ENDPOINT = AUTH_BASE_URL + '/idp/profile/oidc/token'
OIDC_OP_USER_ENDPOINT = AUTH_BASE_URL + '/idp/profile/oidc/userinfo'
OIDC_OP_JWKS_ENDPOINT = AUTH_BASE_URL + '/oidc/keyset.jwk'
OIDC_RP_SIGN_ALGO = 'RS256'
OIDC_USERNAME_ALGO = 'oscauth.backends.generate_username'
OIDC_RP_SCOPES = 'openid email profile'
LOGIN_REDIRECT_URL = SITE_URL
LOGOUT_REDIRECT_URL = SITE_URL
LOGIN_URL = '/oidc/authenticate'

EMAIL_HOST = 'vdc-relay.us-east-2.a.mail.umich.edu'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

SRS_OUTAGE = os.getenv('SRS_OUTAGE', False)
SERVICENOW_EMAIL = os.getenv('SERVICENOW_EMAIL', 'umichdev@service-now.com')

TDX = {
    'URL': os.getenv('TDX_URL'),
    'USERNAME': os.getenv('TDX_USERNAME'),
    'PASSWORD': os.getenv('TDX_PASSWORD'),
}

MCOMMUNITY = {
    'SERVER': os.getenv('MC_SERVER', 'ldap.umich.edu'),
    'USERNAME': os.getenv('MC_USERNAME', 'cn=EAS-OSC-McDirApp001,ou=Applications,o=services'),
    'PASSWORD': os.getenv('MC_PASSWORD', 'N/A'),
}

UM_API = {
    'CLIENT_ID': os.getenv('UM_API_CLIENT_ID'),
    'CLIENT_SECRET': os.getenv('UM_API_CLIENT_SECRET'),
    'AUTH_TOKEN': os.getenv('UM_API_AUTH_TOKEN'),
    'BASE_URL': os.getenv('UM_API_URL'),
}

ROOT_URLCONF = 'project.urls'

TEMPLATES = {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['apps/rte/templates','apps/bom/templates','apps/mbid/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'project.context_processors.menu',
            ],
            'libraries':{
                'index': 'reports.inventory.templatetags.index',
                'tags': 'reports.soc.templatetags.tags',
                'ccr_tags': 'project.templatetags.ccr_tags',
                'descr': 'reports.nonteleph.templatetags.descr',
                'rte_tags': 'apps.rte.templatetags.rte_tags'
            }
        },
},


WSGI_APPLICATION = 'wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE','django.db.backends.postgresql_psycopg2'),
        'NAME': os.getenv('DATABASE_NAME','pgoscdev'),
        'USER': os.getenv('DATABASE_USER','pgoscdevweb'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD','N/A'),
        'HOST': os.getenv('DATABASE_SERVICE_NAME','containernp-pg.aws.vdc.it.umich.edu'),
        'TEST':
        {
        'ENGINE': os.getenv('DATABASE_ENGINE','django.db.backends.postgresql_psycopg2'),
        'NAME': os.getenv('DATABASE_NAME','pgoscdev'),
        'USER': os.getenv('DATABASE_USER','pgoscdevweb'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD','N/A'),
        'HOST': os.getenv('DATABASE_SERVICE_NAME','containernp-pg.aws.vdc.it.umich.edu'),
        },
    },
    'pinnacle': {
        'NAME': os.getenv('ORACLE_DATABASE','pinntst.dsc.umich.edu:1521/pinndev.world'),
        'ENGINE': 'django.db.backends.oracle',
        'USER': os.getenv('ORACLE_USER','PINN_CUSTOM'),
        'PASSWORD': os.getenv('ORACLE_PASSWORD','N/A'),
        'TEST': {
          'NAME': 'pinntst.dsc.umich.edu:1521/pinndev.world',
          'CREATE_DB': False,
          'CREATE_USER': False,
          'USER': os.getenv('ORACLE_USER','PINN_CUSTOM'),
          'PASSWORD': os.getenv('ORACLE_PASSWORD','N/A'),
        }
    },
}


DATABASE_ROUTERS = ['project.settings.DBRouter']


class DBRouter(object):
  def db_for_read(self, model, **hints):

    if model._meta.db_table.startswith('PINN_CUSTOM') or model._meta.db_table.startswith('PS_RATING') or model._meta.db_table.startswith('um_bom'):
      return 'pinnacle'
    return 'default'

  def db_for_write(self, model, **hints):
   
    if model._meta.db_table.startswith('PINN_CUSTOM') or model._meta.db_table.startswith('PS_RATING') or model._meta.db_table.startswith('um_bom'):
      return 'pinnacle'
    return 'default'

  def allow_migrate(self, db, app_label, **hints):
    if app_label == "bom":
        return True

    if db == "pinnacle":
      return False
    else:
      return True



# Password validation
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
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Detroit'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATA_UPLOAD_MAX_NUMBER_FIELDS = 5000

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = '/media' # Use persistent volume in openshift

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

INTERNAL_IPS = ['127.0.0.1']

try:
    from local_settings import *
except ImportError:
    pass