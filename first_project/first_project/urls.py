from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # 管理画面へのアクセスパス
    path('admin/', admin.site.urls),

    # choco_paletteアプリのURL設定を読み込む
    path('', include('choco_palette.urls')), 
]

# デバッグ環境内のみの設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)