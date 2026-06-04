from django.db import models
from django.contrib.auth.models import User

# ユーザープロフィール
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    introduction = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nickname

# 投稿の基本情報
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# 投稿画像（一つの投稿に複数の画像が紐づく想定）
class PostPhoto(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    # ここに upload_to='posts/' を指定してフォルダを分けます！
    photo = models.ImageField(upload_to='posts/')