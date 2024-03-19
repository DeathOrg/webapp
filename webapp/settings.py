import os

# Django settings
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', False) == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'myapp',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'myapp.middleware.RequestIDMiddleware',
    'myapp.middleware.CustomHeadersMiddleware',
    'myapp.middleware.DatabaseCheckMiddleware',
]

ROOT_URLCONF = 'webapp.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'webapp.wsgi.application'

# MySQL Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        # Other authentication classes...
    ],
    # Other DRF settings...
}

import structlog

# Create the directory if it doesn't exist
LOG_BASE_DIR = os.getenv('LOG_DIR', 'var/log')
LOG_DIR = os.path.join(LOG_BASE_DIR, os.getenv('APP_NAME', 'myapp'))
# os.makedirs(LOG_DIR, exist_ok=True)

# Custom processor to rename the 'level' field to 'severity'
def rename_level_to_severity(logger, method_name, event_dict):
    if 'level' in event_dict:
        event_dict['severity'] = event_dict.pop('level')
    return event_dict

# Configure structlog
def configure_structlog():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            rename_level_to_severity,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

configure_structlog()

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'file': {
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, os.getenv('LOG_FILE_NAME', 'app.log')),
            'when': 'D',  # Rotate daily
            'interval': 1,  # Rotate every day
            'backupCount': 10,  # Keep up to 10 log files
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}
