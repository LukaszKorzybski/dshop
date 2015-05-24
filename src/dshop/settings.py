# -*- coding: utf-8 -*-
#
# Django settings for dshop project.

# Values in this module are overriden with respective values from
# dshop.local_settings module if such exist.
# 
# Put any settings that are local for your specific deployment into dshop.settings_local module.
#
# Note: dshop.main.__init__ module initializes application at startup

import os

# try to import local settings
try:
    from dshop import settings_local
except ImportError:
    pass

# Are we running under Jython or CPython?
try:
    import java.lang
    JYTHON = True
except ImportError:
    JYTHON = False


# Load local settings if avaialable, otherwise use provided value
def use_local(**assigns):
    for k in assigns:
        if 'settings_local' in globals():
            globals()[k] = getattr(settings_local, k, assigns[k])
        else:
            globals()[k] = assigns[k]


# Production / debug settings
# ON_PRODUCTION controls things like Analytics inclusion, SSL, etc.
# TODO maybe it would be better to control these things directly, to have more control?
use_local(ON_PRODUCTION = False)
use_local(DEBUG = True)
TEMPLATE_DEBUG = DEBUG


# App root directory path. You absolutely have to set it in your local settings or shell env.
use_local(WEBAPP_ROOT_DIR = '')
WEBAPP_SRC_DIR = os.path.join(WEBAPP_ROOT_DIR, 'src')

# unique shop id, used to generate database name, search engine index name, etc...
use_local(SHOP_ID = 'devel')

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

INTERNAL_IPS = ('127.0.0.1',)

MANAGERS = ADMINS

if JYTHON:
    DATABASE_ENGINE = 'doj.backends.zxjdbc.postgresql'
else:
    DATABASE_ENGINE = 'postgresql_psycopg2'

DATABASE_NAME = 'dshop_'+SHOP_ID                # Or path to database file if using sqlite3.
DATABASE_USER = 'dshop'                         # Not used with sqlite3.
DATABASE_PASSWORD = 'dshop'                     # Not used with sqlite3.
DATABASE_HOST = 'localhost'                         # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''                                  # Set to empty string for default. Not used with sqlite3.

# WF-MAG Database
WFMAG_DB_NAME = 'DEV'
WFMAG_DB_USER = 'dev'
WFMAG_DB_PASSWORD = 'dev'
WFMAG_DB_HOST = 'localhost'
WFMAG_ID_CENY = 4
WFMAG_ID_MAGAZYNU = 1

# Sphinx server
SPHINX_HOST = 'localhost'
SPHINX_PORT = 9312

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Warsaw'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'pl'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True
FORMAT_MODULE_PATH = 'dshop.formats'
USE_THOUSAND_SEPARATOR = False

# Application URL prefix (without trailing slash)
use_local(URL_PREFIX = "")

# Application host name, used by mailing subsystem, etc.
HOST_NAME = 'localhost:8000'

# SSL protocol ('https' for production 'http' for development, used by mailing subsystem)
SSL_PROTO = 'https' if ON_PRODUCTION else 'http'

# Url of login and auth view
LOGIN_URL = URL_PREFIX + '/logowanie/'
AUTH_URL = URL_PREFIX + '/autoryzacja/'

# Where to redirect after client logout
LOGIN_REDIRECT_URL = URL_PREFIX + "/"

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(WEBAPP_SRC_DIR, 'static/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = URL_PREFIX + '/static/'

DEFAULT_FROM_EMAIL = 'Dshop <dshop@localhost>'
EMAIL_HOST = 'localhost'
EMAIL_FILE_PATH = os.path.join(WEBAPP_ROOT_DIR, 'log/email-debug') # used by development instances by filebased.EmailBackend

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = URL_PREFIX + '/static/admin/'

ADMIN_PREFIX = 'new-admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'dshop.main.middleware.DShopRequestMiddleware',
    'dshop.main.middleware.ThreeLevelAuthMiddleware',
    'dshop.main.middleware.ShoppingCartMiddleware'
    #'debug_toolbar.middleware.DebugToolbarMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "dshop.main.context_processors.common",
    "dshop.main.context_processors.system_params",
    "dshop.main.context_processors.page_fragments",
    "dshop.cookies_policy.context_processors.common"
)


ROOT_URLCONF = 'dshop.urls'

TEMPLATE_DIRS = (
    os.path.join(WEBAPP_SRC_DIR, "templates"),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sessions',
    'django.contrib.admin',
    'mptt',
    'compress',
    #'debug_toolbar',
    'dshop.main'
]

if JYTHON:
    INSTALLED_APPS.append('doj')


# Max age of session cookies in seconds (6 months)
SESSION_COOKIE_AGE = 15552000

# Max age of second level authorization since user login time (6 hours).
#
# Second level authorization allows customers to place orders and modify profile.
# It lasts much shorter than first level authorization which lasts from user login
# till session expiration.
#
# First level authorization allows customers to see their orders, profile, discounts, proposals etc.
#
SND_LEVEL_AUTH_AGE = 21600
AUTH_PROFILE_MODULE = 'main.UserProfile'

# Static files versioning. 'qs' - append query string, 'name' - alter file name
STATICS_VERSIONING = 'qs'

# Dshop frontend application settings
RANDOM_ARTICLES_COUNT = 5

# Application wide page size settings (articles, orders, discounts, etc)
PAGE_SIZE = 20

# Max number of results returned from full-text search engine
FTS_MAX_RESULTS = 2000

# Stock management software may or may not round order item sum prices before calculating
# sum order price.
ORDER_ROUND_PRICE_BEFORE_SUM = False

# DotPay.pl online payments
DOTPAY_USER_ID = ''
DOTPAY_PIN = ''
DOTPAY_SELLER = u""
DOTPAY_URL = ''
DOTPAY_TYPE = '0'
DOTPAY_BUTTON_TEXT = u"Powrót do sklepu"

# PayPal online payments
PAYPAL_ACCOUNT = u''
PAYPAL_URL = u'https://www.sandbox.paypal.com/cgi-bin/webscr'

GOOGLE_ANALYTICS = 'UA-XXX'

# Django-compress settings
COMPRESS = not DEBUG
COMPRESS_VERSION = True
COMPRESS_CSS_FILTERS = None
COMPRESS_CSS = {
        'all-css' : {
            'source_filenames' : ('css/base.css',
                                  'css/dshop.css',
                                  'lib/facebox/facebox.css',
                                  'lib/flash_tube/jFlashTube.css'),
            'output_filename' : 'css/all_comp.r?.css'
        },
        'ie8-css' : {
            'source_filenames' : ('css/ie8.css', ),
            'output_filename' : 'css/ie8_comp.r?.css'
        },
        'iesucks-css' : {
            'source_filenames' : ('css/iesucks.css', ),
            'output_filename' : 'css/iesucks_comp.r?.css'
        }
}
COMPRESS_JS = {
        'libs' : {
            'source_filenames' : ('lib/jquery.js',
                                  'lib/json2.js',
                                  'lib/swfobject.js',
                                  'lib/facebox/facebox.js',
                                  'lib/flowplayer/flowplayer-3.0.6.min.js',
                                  'lib/flash_tube/jFlashTube.js',
                                  'lib/jquery.raty.js'),
            'output_filename' : 'js/lib_comp.r?.js'
        },
        'dshop' : {
            'source_filenames' : ('js/init.js', 'js/plugins.js', 'js/pages.js'),
            'output_filename' : 'js/dshop_comp.r?.js'
        }
}

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

# are we running inside servlet container? (we run inside Tomcat only on production)
try:
    import javax.servlet
    TOMCAT = True
except ImportError:
    TOMCAT = False


# Load local settings if dshop.settings_local module exist
try:
    from dshop.settings_local import *
except ImportError:
    pass
