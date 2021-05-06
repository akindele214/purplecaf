from nwucaf.helpers.settings_helper import get_env_variable

DEFAULT_FILE_STORAGE = 'storages.backends.dropbox.DropBoxStorage'

DROPBOX_OAUTH2_TOKEN = get_env_variable('DROPBOX_ACCESS_TOKEN', 'oIy_jyuVKpIAAAAAAAAAATc1AHHJSfwmyZD4X12IFiEaLhi51tZpst9GNuBnQIAC')

DROPBOX_ROOT_PATH = '/Public'
