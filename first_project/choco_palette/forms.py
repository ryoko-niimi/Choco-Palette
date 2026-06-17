from django import forms
from .models import Profile
from django.contrib.auth.models import User
from .models import Post
from django.contrib.auth.forms import AuthenticationForm

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
    
# テイスティング投稿用フォーム
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['chocolate_name','brand_name','cacao_percentage',
                  'tasting_date', 'favorite_rate', 'tasting_comment',
                  'private_memo', 'status', 'taste_tags', 'aroma_tags'
        ]
        labels = {
            'chocolate_name': '商品名',
            'brand_name': 'ブランド名',
            'cacao_percentage': 'カカオ含有率',
            'tasting_date': 'テイスティング日',
            'favorite_rate': 'お気に入り度',
            'tasting_comment': 'テイスティングコメント',
            'private_memo': 'プライベートメモ',
            'status': '公開範囲',
            'taste_tags': '味タグ',
            'aroma_tags': '香りタグ',
        }

# ログイン用フォーム
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='メールアドレス', widget=forms.TextInput(attrs={'autofocus': True}))