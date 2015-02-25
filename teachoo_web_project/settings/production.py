DATABASES = { 
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }   
}

DEBUG = True
TEMPLATE_DEBUG = True

# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] = dj_database_url.config()

# Enable Connection Pooling
#DATABASES['default']['ENGINE'] = 'django_postgrespool'

ALLOWED_HOSTS = ['*']


#STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

#django-allauth email
ACCOUNT_EMAIL_VERIFICATION = ("mandatory")
