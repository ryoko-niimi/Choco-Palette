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
    
# テイスティング投稿用フォーム 編集フォーム
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['chocolate_name', 'brand_name', 'cacao_percentage',
                  'tasting_date', 'favorite_rate', 'tasting_comment',
                  'private_memo', 'status', 'taste_tags', 'aroma_tags'
        ]
        widgets = {
            'chocolate_name': forms.TextInput(attrs={'placeholder': '商品名を入力してください', 'class': 'form-control'}),
            'brand_name': forms.TextInput(attrs={'placeholder': 'ブランド名を入力してください', 'class': 'form-control'}),
            'cacao_percentage': forms.NumberInput(attrs={'placeholder': '不明な場合は空欄OK', 'class': 'form-control'}),
            'tasting_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tasting_comment': forms.Textarea(attrs={'placeholder': '', 'rows': 4, 'class': 'form-control'}),
            'private_memo': forms.Textarea(attrs={'placeholder': '自分用メモ（非公開）', 'rows': 4, 'class': 'form-control'}),
            'status': forms.RadioSelect(choices=[('public', '公開'), ('private', '非公開')]),
            'favorite_rate': forms.HiddenInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. 必須バッジの定義
        badge = '<span class="required-badge">必須</span>'
        
        # 2. ラベルにバッジを結合
        self.fields['chocolate_name'].label = f'商品名{badge}'
        self.fields['brand_name'].label = f'ブランド名{badge}'
        self.fields['status'].label = f'公開範囲{badge}'
        self.fields['cacao_percentage'].label = f'カカオ含有率{badge}'
        self.fields['tasting_date'].label = f'テイスティング日{badge}'
        
        # 3. その他（バッジなしの項目）のラベルを日本語に設定
        self.fields['favorite_rate'].label = 'お気に入り度'
        self.fields['tasting_comment'].label = 'テイスティングコメント'
        self.fields['private_memo'].label = 'プライベートメモ'
        self.fields['taste_tags'].label = '味タグ'
        self.fields['aroma_tags'].label = '香りタグ'
        
        # 4. カカオ含有率は必須入力をオフにする（バッジだけ表示）
        self.fields['cacao_percentage'].required = False
        
        # 5. 編集時の日付読み取り専用設定
        if self.instance.pk:
            self.fields['tasting_date'].widget.attrs['readonly'] = True
            self.fields['tasting_date'].widget.attrs['style'] = 'background-color: #f0f0f0; cursor: not-allowed;'
       



# ログイン用フォーム
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='メールアドレス', widget=forms.TextInput(attrs={'autofocus': True}))