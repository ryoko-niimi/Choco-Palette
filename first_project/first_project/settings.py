import os
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトの基準となる場所（BASE_DIR）
BASE_DIR = Path(__file__).resolve().parent.parent

#.envファイルを読み込む
load_dotenv(BASE_DIR / '.env')

# 開発用の設定 '*'
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-63rya_1s$3_+2k(lly=qw1qw5@bmnag5q)p(+7es$&fe3y3b&1')
DEBUG = True
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'ryokoniimi.pythonanywhere.com']

# アプリケーションの登録リスト
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'choco_palette',
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

ROOT_URLCONF = 'first_project.urls'

# テンプレート設定
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'first_project.wsgi.application'

# データベース設定
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 認証バックエンドの設定（メールアドレスでログイン）
AUTHENTICATION_BACKENDS = [
    'choco_palette.backends.EmailAuthBackend',  
    'django.contrib.auth.backends.ModelBackend', 
]

# パスワードバリデーション
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS': {'min_length': 8,}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    ]


# 国際化設定
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True


# 静的ファイル設定
STATIC_URL = '/static/'
STATICFILES_DIRS = [ 
    BASE_DIR / 'choco_palette/static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'


# メディアファイル設定
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# パスワード再設定メール設定（console↔smtpに直す）
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

#ログイン後の遷移先
LOGIN_REDIRECT_URL = 'choco_palette:post_list'
#未ログイン時に促す遷移先はログイン画面
LOGIN_URL = 'choco_palette:login'


