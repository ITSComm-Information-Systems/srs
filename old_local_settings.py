pinnacle = 'pinndev'
default = 'srsdev'

WSGI_APPLICATION = 'project.wsgi.application'

DATABASES = {
   'local': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': 'local_restore',
       'USER': 'pgoscdevweb',
       'PASSWORD': '4zWV4bpup350',
       'HOST': '10.196.41.184',
       'PORT': 5432
   },
   'srsdev': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': 'pgoscdev',
       'USER': 'pgoscdevweb',
       'PASSWORD': '4zWV4bpup350',
       'HOST': '10.196.41.184',
       'PORT': 5432
   },
   'srsqa': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': 'pgoscqa',
       'USER': 'pgoscqaweb',
       'PASSWORD': 'V42Re7WBgVS2',
       'HOST': 'containernp-pg.aws.vdc.it.umich.edu'
   },
   'srsPROD': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': 'pgsrsprod',
       'USER': 'pgsrsprodweb',
       'PASSWORD': 'Uf4QLXK5PobQ',
       'HOST': 'containerprod-pg.aws.vdc.it.umich.edu'
   },
   'pinnPROD': {
       'NAME': 'pinntst-ora.dsc.umich.edu/:1521/pinnprod',  #pinndev_blade if you have a tnsnames file
       'ENGINE': 'django.db.backends.oracle',
       #'USER': 'RMTITCOMOSC_DJ_PINNPROD1',
       #'PASSWORD': 'xF8Imnsa4',
 
       'USER': 'PINN_CUSTOM',
       'PASSWORD': 'tY7sAejb'
   },
   'pinnqa': {
       'NAME': 'pinntst-ora.dsc.umich.edu:1521/pinnqa',  #pinndev_blade if you have a tnsnames file
       'ENGINE': 'django.db.backends.oracle',
       'USER': 'PINN_CUSTOM',
       'PASSWORD': 'gv3psws5',
   },
   'pinndev': {
       'NAME': 'pinntst-ora.dsc.umich.edu:1521/pinndev',  #pinndev_blade if you have a tnsnames file
       #'NAME': 'PINN_CUSTOM',
       'ENGINE': 'django.db.backends.oracle',
       'USER': 'PINN_CUSTOM',
       'PASSWORD': 'wpfx8rea',
       'TEST': {
         'NAME': 'pinntst-ora.dsc.umich.edu:1521/pinndev', # or pinndev_blade
         'CREATE_DB': False,
         'CREATE_USER': False,
         'USER': 'PINN_CUSTOM',
         'PASSWORD': 'wpfx8rea'
       }
   },
}

print(f'Use {pinnacle} and {default}')

DATABASES['pinnacle'] = DATABASES[pinnacle]
DATABASES['default'] = DATABASES[default]


MEDIA_ROOT = '/Users/djamison/oscmedia' 



OIDC_RP_CLIENT_ID='b976c852-20f0-444c-95f9-5924757143a6'
OIDC_RP_CLIENT_SECRET='4d451a20-1f9f-46a9-b676-5736f5b3c05d'


# Prod
#OIDC_RP_CLIENT_ID = '38e946e0-dfc8-4b4f-b5f7-3dcadaa94ebb'
#OIDC_RP_CLIENT_SECRET = 'd8d538eb-48cd-4a24-82ec-767eb393b657'
#AUTH_BASE_URL = 'https://shibboleth.umich.edu'


MCOMMUNITY = {
    'SERVER': 'ldap.umich.edu',
    'USERNAME': 'cn=EAS-OSC-McDirApp001,ou=Applications,o=services',
    'PASSWORD': '3wFe7XaCk6rF',
}

UM_API = {
    'CLIENT_ID': '2d52f5e4-7404-43c4-968c-4e84548d331b',
    'CLIENT_SECRET': 'cH4bB0nG3eG4vL0jF2pM4xE0uT5xI1cR3yK5nM3iV5rH4mL2lU',
    'BASE_URL': 'https://apigw-tst.it.umich.edu',
    'AUTH_TOKEN': 'MmQ1MmY1ZTQtNzQwNC00M2M0LTk2OGMtNGU4NDU0OGQzMzFiOmNINGJCMG5HM2VHNHZMMGpGMnBNNHhFMHVUNXhJMWNSM3lLNW5NM2lWNXJING1MMmxV',
}


UM_API_PRODUCTION_ONLY = {
    'CLIENT_ID': 'bc7954e1-6b0b-4fd0-86d6-983b7ab2ca6e',
    'CLIENT_SECRET': 'Q0aP6oW5mU3rK0aP4gX7yH5qF4vC2dC5dH0dW1sP4kC0eM0oG4',
    'BASE_URL': '.......https://apigw.it.umich.edu',
    'AUTH_TOKEN': 'YmM3OTU0ZTEtNmIwYi00ZmQwLTg2ZDYtOTgzYjdhYjJjYTZlOlEwYVA2b1c1bVUzckswYVA0Z1g3eUg1cUY0dkMyZEM1ZEgwZFcxc1A0a0MwZU0wb0c0',
}

WPS_API = {
    'CLIENT_ID': 'dbMvqRah0yqLsRHVRvQ9cKVnv1YODSBkemXv8xjd',
    'CLIENT_SECRET': 'bZdzW9cIIbvMk9TddbQGa2xGbGrfIPYHfSA79SxyC0lNzjRvfzeAwOBHxYVvqABhrWrTIQ8lOgkBFWAEZeORJy3FveH0NzIeD808OI5pAR57GAK90FgLsBcxVHj7FHse',
    'BASE_URL': 'https://kiri-qa.webplatformsunpublished.umich.edu',
    'AUTH_TOKEN': 'ZGJNdnFSYWgweXFMc1JIVlJ2UTljS1ZudjFZT0RTQmtlbVh2OHhqZDpiWmR6VzljSUlidk1rOVRkZGJRR2EyeEdiR3JmSVBZSGZTQTc5U3h5QzBsTnpqUnZmemVBd09CSHhZVnZxQUJocldyVElROGxPZ2tCRldBRVplT1JKeTNGdmVIME56SWVEODA4T0k1cEFSNTdHQUs5MEZnTHNCY3hWSGo3RkhzZQ==',
}

#python -m smtpd -n -c DebuggingServer localhost:1025

ALLOWED_HOSTS = ['*']

DEBUG = True

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_USE_TLS = False

SITE_URL = 'http://127.0.0.2:8080'