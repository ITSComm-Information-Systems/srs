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

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', True)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'oscauth',
    'project',
    'django.contrib.admin',
    'django.contrib.auth',
    'mozilla_django_oidc',  # Load after auth
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',
    'order',
    'pages',
    'reports',
]

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
    'mozilla_django_oidc.auth.OIDCAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
    'oscauth.backends.SuBackend',
]

ROOT_URLCONF = 'project.urls'

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
                'project.context_processors.menu',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE','django.db.backends.postgresql_psycopg2'),
        'NAME': os.getenv('DATABASE_NAME','pgoscdev'),
        'USER': os.getenv('DATABASE_USER','postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD','w94zLR2dkkfo'),
        'HOST': os.getenv('DATABASE_SERVICE_NAME','pgoscdev.cvwq7quwqs3k.us-east-2.rds.amazonaws.com'),
        #'PORT': '15432',
    },
    'pinnacle': {
        'NAME': os.getenv('ORACLE_DATABASE','pinndev_blade.world'),
        'ENGINE': 'django.db.backends.oracle',
        'USER': os.getenv('ORACLE_USER','PINN_CUSTOM'),
        'PASSWORD': os.getenv('ORACLE_PASSWORD','wpfx8rea'),
        'TEST': {
          'NAME': 'pinntst.dsc.umich.edu:1521/pinndev.world',
          'CREATE_DB': False,
          'CREATE_USER': False,
          'USER': os.getenv('ORACLE_USER','PINN_CUSTOM'),
          'PASSWORD': os.getenv('ORACLE_PASSWORD','wpfx8rea'),
        }
    },
}

DATABASE_ROUTERS = ['project.settings.DBRouter']


# mozilla-django-oidc
SITE_URL = os.getenv('SITE_URL')
OIDC_RP_CLIENT_ID = os.getenv('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET')
OIDC_OP_AUTHORIZATION_ENDPOINT = 'https://shibboleth.umich.edu/idp/profile/oidc/authorize'
OIDC_OP_TOKEN_ENDPOINT = 'https://shibboleth.umich.edu/idp/profile/oidc/token'
OIDC_OP_USER_ENDPOINT = 'https://shibboleth.umich.edu/idp/profile/oidc/userinfo'
OIDC_OP_JWKS_ENDPOINT = 'https://shibboleth.umich.edu/oidc/keyset.jwk'
OIDC_RP_SIGN_ALGO = 'RS256'
LOGIN_REDIRECT_URL = SITE_URL
LOGOUT_REDIRECT_URL = SITE_URL
LOGIN_URL = '/oidc/authenticate'

class DBRouter(object):
  def db_for_read(self, model, **hints):

    if model._meta.db_table.startswith('PINN_CUSTOM'):
      return 'pinnacle'
    return 'default'

  def db_for_write(self, model, **hints):
    return 'default'

  def allow_migrate(self, db, app_label, **hints):
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

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

INTERNAL_IPS = ['127.0.0.1']
