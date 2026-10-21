"""
Django settings for ResumeIQ project.
Generated for ResumeIQ – AI Resume Analyzer SaaS application.
"""

import os
from pathlib import Path

# Load environment variables from .env if python-dotenv is present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-resumeiq-mini-project-secure-key-2026-production-ready'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0,testserver').split(',')
    if host.strip()
]
# Ensure testserver is always permitted for test clients
if 'testserver' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ResumeIQ App
    'analyzer.apps.AnalyzerConfig',
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

ROOT_URLCONF = 'resumeiq.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'resumeiq.wsgi.application'
ASGI_APPLICATION = 'resumeiq.asgi.application'

# Database: SQLite for lightweight zero-config persistence
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'analyzer' / 'static',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File Upload Security & Memory-Only Handling (Zero Disk Persistence)
# Up to 5 MB processed entirely in RAM, never persisted to disk or logged
MAX_UPLOAD_SIZE_MB = int(os.environ.get('MAX_UPLOAD_SIZE_MB', 5))
FILE_UPLOAD_MAX_MEMORY_SIZE = MAX_UPLOAD_SIZE_MB * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = (MAX_UPLOAD_SIZE_MB + 2) * 1024 * 1024

# AI Service Configuration
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'auto').lower()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash').strip()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini').strip()
OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', '').strip()
