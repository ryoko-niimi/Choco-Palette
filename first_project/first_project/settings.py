
import os
import sys

# 【特殊設定】フォルダの住所（パス）を自動調整する
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path

# --- プロジェクトの基準となる「実家の住所」（BASE_DIR） ---
# プロジェクト内のパスを指定するときは `BASE_DIR / 'フォルダ名'` のように pathlib を使います。
BASE_DIR = Path(__file__).resolve().parent.parent


# --- 開発用のクイックスタート設定（本番公開時は注意が必要な項目） ---
# 詳細はチェックリストを参照: https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/


SECRET_KEY = 'django-insecure-63rya_1s$3_+2k(lly=qw1qw5@bmnag5q)p(+7es$&fe3y3b&1'

DEBUG = True

# アプリへのアクセスを許可するホスト名（ドメイン）のリスト。
ALLOWED_HOSTS = []


# --- アプリケーションの定義 ---

# このDjangoプロジェクトで動かす「アプリ」の登録リスト
INSTALLED_APPS = [
    'django.contrib.admin',          # 管理画面
    'django.contrib.auth',           # ユーザー認証（ログインなど）
    'django.contrib.contenttypes',   # データ型管理の仕組み
    'django.contrib.sessions',       # セッション管理（ログイン状態の維持）
    'django.contrib.messages',       # メッセージ通知機能
    'django.contrib.staticfiles',    # 静的ファイル（CSSや画像）の管理
    'choco_palette',                 
]

# リクエストとレスポンスの間に挟まる、セキュリティや便利機能の詰め合わせ（ミドルウェア）
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ルート（一番最初）のURL設定ファイルの場所
ROOT_URLCONF = 'first_project.urls'

# 画面（HTML）を組み立てる「テンプレート」の設定
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], #templatesフォルダを見に行く設定
        'APP_DIRS': True,                  # 各アプリ内のtemplatesフォルダも自動で探す
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WebサーバーとDjangoを繋ぐための設定（WSGI）
WSGI_APPLICATION = 'first_project.wsgi.application'


# --- データベースの設定 ---
# 詳細はドキュメントを参照: https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # 手軽に使えるSQLite3データベース
        'NAME': BASE_DIR / 'db.sqlite3',         # データベースファイルの保存場所
    }
}


# --- パスワードのバリデーション（安全性のチェック） ---
# ユーザー登録時に、簡単すぎるパスワードをブロックする設定
# 詳細はドキュメントを参照: https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', # ユーザー名と似たパスワードを禁止
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',           # 最低文字数のチェック
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',          # よくある簡単なパスワードを禁止
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',         # 数字だけのパスワードを禁止
    },
]


# --- 国際化（言語と時間の設定） ---
# 詳細はドキュメントを参照: https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'ja'             

TIME_ZONE = 'Asia/Tokyo'         

USE_I18N = True                  # 翻訳機能を使用する

USE_TZ = True                    # タイムゾーン（時差）を考慮する


# --- 静的ファイル（CSS、JavaScript、デザイン用画像）の設定 ---
STATIC_URL = 'static/'


# --- メディアファイル（ユーザーがアップロードする画像など）の設定 ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

