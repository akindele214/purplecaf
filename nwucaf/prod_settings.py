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
    get_env_variable('DATABASE_URL', 'postgres://zzlbguznvikrcs:02b5db8d846011a570425ce73c29be16eb77fbac3eedb2adbf6bad167a27f728@ec2-3-215-57-87.compute-1.amazonaws.com:5432/db1og9cm28l1fd'), conn_max_age=600)

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

VENV_PATH = os.path.dirname(BASE_DIR)
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_in_env')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static_in_env')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
