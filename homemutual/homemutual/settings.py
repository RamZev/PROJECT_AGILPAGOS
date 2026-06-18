import locale
from pathlib import Path
from dotenv import load_dotenv
from os import path, getenv, makedirs

#-- Cargar las variables de entorno del archivo .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

#-- Crear directorio de logs si no existe.
LOGS_DIR = path.join(BASE_DIR, 'logs')
if not path.exists(LOGS_DIR):
	makedirs(LOGS_DIR, exist_ok=True)


#-- Detectar el entorno (development o production)
ENVIRONMENT = getenv('ENVIRONMENT', 'development')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENVIRONMENT == 'development'

#-- Configuración de hosts permitidos según entorno.
#-- Obtener hosts del .env y limpiar espacios en blanco.
allowed_hosts_raw = getenv('ALLOWED_HOSTS', '')
if allowed_hosts_raw:
	#-- Limpiar espacios y separar por coma.
	ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_raw.split(',') if host.strip()]
else:
	#-- Valores por defecto según entorno.
	if ENVIRONMENT == 'production':
		ALLOWED_HOSTS = []
	else:
		ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	#---------------------
	'apps.usuarios',
    'apps.maestros',
    'apps.menu',
	#---------------------
	'apps.consultas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'homemutual.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Carpeta templates a nivel del proyecto
			path.join(BASE_DIR, 'templates')    
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
				'context_processors.context_processors_menu.menu_context',
				'context_processors.context_processors_empresa.empresa_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'homemutual.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
		'NAME': path.join(BASE_DIR, 'data', 'homemutual.db'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True  # Internacionalización.
USE_L10N = True  # Localización.

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (path.join(BASE_DIR, 'static'),)
STATIC_ROOT = path.join(BASE_DIR, 'staticfiles')

# Archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# OBLIGATORIO: PERSONALIZACIÓN DEL MODELO USUARIOS
AUTH_USER_MODEL = 'usuarios.User'

#-- URL de redireccionamiento de la vista para iniciar sesión.
LOGIN_URL = '/usuarios/sesion/iniciar/'

#-- URL de redireccionamiento una vez logueado.
LOGIN_REDIRECT_URL = '/'

#-- URL de redireccionamiento al cerrar sesión.
LOGOUT_REDIRECT_URL = '/usuarios/sesion/iniciar/'

#-- Para evitar el "secuestro" de la sesión de usuario por JavaScript desde el front.
SESSION_COOKIE_HTTPONLY = True

#-- La sesión del usuario se cierra al cerrar el navegador.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

#-- Configuración del locale para Argentina/España.
try:
	locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')  # Linux/Mac
except locale.Error:
	locale.setlocale(locale.LC_ALL, 'spanish')      # Windows como fallback


# ============================================================================
# CONFIGURACIÓN DE CORREO ELECTRÓNICO
# ============================================================================

#-- Configuraciones comunes para ambos entornos (pueden ser sobreescritas por el .env según el entorno).

#-- Backend de correo.
EMAIL_BACKEND = getenv('EMAIL_BACKEND', None)

#-- Dirección de correo desde la cual se enviarán los emails del sistema.
DEFAULT_FROM_EMAIL = getenv('DEFAULT_FROM_EMAIL', None)

#-- Prefijo para asuntos de correo (útil para identificar emails del sistema).
EMAIL_SUBJECT_PREFIX=getenv('EMAIL_SUBJECT_PREFIX', None)

#-- Tiempo de expiración del token de recuperación (24 horas, en segundos).
PASSWORD_RESET_TIMEOUT = int(getenv('PASSWORD_RESET_TIMEOUT', 0))

#-- Timeout para envío de emails (en segundos).
EMAIL_TIMEOUT = int(getenv('EMAIL_TIMEOUT', 0))

#-- Configuración según el entorno (development o production).
if ENVIRONMENT == 'production' or ENVIRONMENT == 'development':
	#-- Configuración para producción.
	EMAIL_HOST = getenv('EMAIL_HOST', None)
	EMAIL_PORT = int(getenv('EMAIL_PORT', 0))
	EMAIL_USE_TLS = getenv('EMAIL_USE_TLS', 'True') == 'True'
	EMAIL_USE_SSL = getenv('EMAIL_USE_SSL', 'False') == 'True'
	EMAIL_HOST_USER = getenv('EMAIL_HOST_USER', None)
	EMAIL_HOST_PASSWORD = getenv('EMAIL_HOST_PASSWORD', None)