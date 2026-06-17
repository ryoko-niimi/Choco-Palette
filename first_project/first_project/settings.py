import os
from pathlib import Path

# プロジェクトの基準となる場所（BASE_DIR）
BASE_DIR = Path(__file__).resolve().parent.parent

# 開発用の設定
SECRET_KEY = 'django-insecure-63rya_1s$3_+2k(lly=qw1qw5@bmnag5q)p(+7es$&fe3y3b&1'
DEBUG = True
ALLOWED_HOSTS = []

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

# パスワードバリデーション
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 国際化設定
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

# 静的ファイル設定
STATIC_URL = 'static/'

# メディアファイル設定
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# メール設定（SMTP）
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'test1@example.com'
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'

#ログイン後の遷移先
LOGIN_REDIRECT_URL = 'choco_palette:post_list'
#未ログイン時に促す遷移先はログイン画面
LOGIN_URL = 'choco_palette:login'

# 認証の設定 
# ユーザー名ではなく「メールアドレス」でログインできるようにするカスタムバックエンド
AUTHENTICATION_BACKENDS = [
    'choco_palette.backends.EmailBackend', 
    'django.contrib.auth.backends.ModelBackend',
]