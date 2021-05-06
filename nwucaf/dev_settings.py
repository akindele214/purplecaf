import os
from nwucaf.base_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q*_(0+fa=rkbmjie=#huzhs@t21em9$4=j-+mzqe4ek0l*m+sz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'nwucaf.db'),
    }
}
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = [
    '127.0.0.1',
]

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'nwucaf/static_in_env'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": "BLo9X1JCqK1bP36UutiGQgp2MACheO3iYBMdEQ6qw17htY_RrGmtWn0vgEbkPj5-BwDc8BAoMIFNO969-lehRq8",
    "VAPID_PRIVATE_KEY":"WIN1ntQB1-NXiVkrZP58TgFB7dr-gJJw5DnUnesRc1k",
    "VAPID_ADMIN_EMAIL": "yaomingnakel@gmail.com"
}

