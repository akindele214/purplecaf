from nwucaf.helpers.settings_helper import get_env_variable

# STRIPE
STRIPE_TEST_SECRET_KEY = 'sk_test_51HaZaGLCh1XB8iWQXVO61bC9QYAtqWXFiy5gale7rtqiYFrOvo09W2Nx9RFTMDQTzCyo3gNRC2cU741r3Mlgs6w9005TnAl8zU'

STRIPE_TEST_PUBLISHABLE_KEY = 'pk_test_51HaZaGLCh1XB8iWQF7gM0tGytNkVHtxUukJY43cQKPpXLL2frA4DRweI3hOe1AfWUyp2fvtvPtXfGyemnui8Wd4C0059DtvwzW'

STRIPE_SECRET_KEY = get_env_variable('STRIPE_TEST_SECRET_KEY', STRIPE_TEST_SECRET_KEY)

STRIPE_PUBLISHABLE_KEY = get_env_variable('STRIPE_TEST_PUBLISHABLE_KEY', STRIPE_TEST_PUBLISHABLE_KEY)