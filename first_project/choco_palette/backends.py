from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # ログイン時に入力されたものを email として検索する
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        
        # パスワードが合っているか確認
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None