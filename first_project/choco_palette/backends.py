#メールアドレスをログイン判定にするバックエンド

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailAuthBackend(ModelBackend):
    """
    ユーザー名の代わりにメールアドレスを使ってログインを判定するカスタムバックエンド
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        
        # 画面の入力欄から送られてきた値（usernameという変数に入っています）をメールアドレスとして扱う
        email = username or kwargs.get('email')
        
        try:
            # 入力されたメールアドレスを持つユーザーを検索
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

        # パスワードが合致しているかチェック
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None