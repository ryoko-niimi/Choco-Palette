from django.contrib import admin
from .models import Profile  #作成したProfileの設計図を読み込み

# 管理画面にProfileを表示する設定
admin.site.register(Profile)