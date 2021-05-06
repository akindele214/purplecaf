import os

import dj_database_url

from nwucaf.base_settings import *
from nwucaf.settings.local.email_settings import *
from nwucaf.settings.packages.dropbox_settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable("SECRET_KEY", '#+-oo*28)_orl_dieyal9j!^*c3c=#mnal8+v3)v3fl!!wyem@')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_env_variable("DEBUG", "False") == "True"

ALLOWED_HOSTS = ['*']

INSTALLED_APPS.append('storages')
# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {}
DATABASES['default'] = dj_database_url.parse(
    get_env_variable('DATABASE_URL', 'postgres://zwpoiatpncjxef:fc6465fb1a66d9fb5245a800526082f9a989446ea5ce4ffb49fe1dd6eea8c491@ec2-18-215-111-67.compute-1.amazonaws.com:5432/d5f7o8m18dnf77'), conn_max_age=600)

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

VENV_PATH = os.path.dirname(BASE_DIR)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_in_env')]
STATIC_ROOT = os.path.join(VENV_PATH, 'static_in_env')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
