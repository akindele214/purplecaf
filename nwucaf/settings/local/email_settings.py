from nwucaf.helpers.settings_helper import get_env_variable

# Sending email configuration
EMAIL_HOST_USER = get_env_variable("ADMIN_EMAIL_ADDRESS", "no-reply@reportr.co.uk")

EMAIL_HOST_PASSWORD = get_env_variable("ADMIN_EMAIL_PASSWORD", "PASS")

EMAIL_PORT = get_env_variable("EMAIL_PORT", 465)

EMAIL_HOST = get_env_variable("EMAIL_HOST", "mail.reportr.co.uk")

EMAIL_USE_SSL = True

# Admin email configuration
ADMIN_EMAILS = [
    [get_env_variable("ADMIN_FULL_NAME", "Reportr Master"), get_env_variable("ADMIN_EMAIL_ADDRESS", "no-reply@reportr.co.uk")]]

ADMINS = ADMIN_EMAILS

MANAGERS = ADMIN_EMAILS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
