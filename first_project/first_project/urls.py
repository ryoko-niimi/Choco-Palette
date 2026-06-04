from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    # ログインやマイページへ行くための設定
    path('choco_palette/', include('choco_palette.urls')),
    # トップページにアクセスしたら自動的にログイン画面へ飛ばす設定
    path('', lambda request: redirect('choco_palette:login')),
]