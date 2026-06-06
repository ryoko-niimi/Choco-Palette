from django import forms
from .models import Profile
from django.contrib.auth.models import User

# プロフィール設定と編集のフォーム
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nickname', 'image', 'introduction', 'link']

# ユーザー情報（アカウント登録用）のフォーム
class SignupForm(forms.ModelForm):
    # パスワード入力欄を明示的に定義
    password = forms.CharField(widget=forms.PasswordInput, label="パスワード")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="パスワード再入力")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
        # フィールドの表示名を変更
        labels = {
            'username': 'ニックネーム',
            'email': 'メールアドレス',
        }
        
        # パスワード入力欄に属性を追加（セキュリティのため）
        widgets = {
            'password': forms.PasswordInput(),
        }

    # パスワードの一致チェック用メソッド（バリデーション）
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("パスワードと再入力パスワードが一致していません。")
        
        return cleaned_data