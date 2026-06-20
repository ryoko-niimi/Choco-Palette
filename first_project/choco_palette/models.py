from django.db import models
from django.contrib.auth.models import User

# パスワード再設定
class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# ユーザープロフィール
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nickname

# 味タグ
class TasteTag(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

# 香りタグ
class AromaTag(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

# 投稿の基本情報
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chocolate_name = models.CharField(max_length=100)
    brand_name = models.CharField(max_length=100)
    cacao_percentage = models.IntegerField(null=True, blank=True)
    tasting_date = models.DateField(null=True, blank=True)
    favorite_rate = models.IntegerField(default=0)
    tasting_comment = models.TextField()
    private_memo = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    status_choices =(
        (1,"公開"),
        (2,"非公開"),
         )
    status = models.IntegerField(choices=status_choices,default=1)
         
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    taste_tags = models.ManyToManyField(TasteTag, blank=True)
    aroma_tags = models.ManyToManyField(AromaTag, blank=True)
    
    def __str__(self):
        return f"{self.user.username}の投稿 ({self.created_at})"

# 投稿画像
class PostPhoto(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='posts/')
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
       
    def __str__(self):
        return f"{self.post.chocolate_name}の画像({self.created_at})"