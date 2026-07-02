from django.contrib import admin
from .models import Profile, Post, PostPhoto, PasswordReset, TasteTag, AromaTag

# 1. 登録
@admin.register(TasteTag)
class TasteTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(AromaTag)
class AromaTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

# 2. 投稿の管理
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'chocolate_name', 'brand_name', 'created_at')
    # 検索窓に商品名やブランド名も追加
    search_fields = ('user__username', 'chocolate_name', 'brand_name', 'tasting_comment')
    # フィルター（右側の絞り込み）を追加
    list_filter = ('created_at', 'tasting_date')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname')

#その他
admin.site.register(PostPhoto)
admin.site.register(PasswordReset)

