from django import forms
from .models import Profile
from django.contrib.auth.models import User
from .models import Post
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate


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
        # widgetsはここで指定せず、__init__で統一的に指定します
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # すべてのフィールドにクラスを追加し、PasswordInputを明示的に指定
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # パスワード系には必要であればここでも明示可能ですが、今のままでもOKです

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
        
        # 必須にしたいフィールド
        self.fields['chocolate_name'].required = True
        self.fields['brand_name'].required = True
        self.fields['status'].required = True
        self.fields['tasting_date'].required = True
        
        # 空欄OKにしたいフィールド
        self.fields['cacao_percentage'].required = False
        self.fields['tasting_comment'].required = False
        self.fields['private_memo'].required = False
        self.fields['favorite_rate'].required = False

       


# ログイン用フォーム
class EmailLoginForm(AuthenticationForm):
    
    username = forms.EmailField(
        label="メールアドレス",
        widget=forms.EmailInput(attrs={'class': 'custom-input',  'autocomplete': 'username'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


    def clean(self):
        # 画面に入力されたメールアドレスを、安全に「username」という箱から取り出す
        username = self.cleaned_data.get('username') 
        password = self.cleaned_data.get('password') 

        if username and password:
            user = User.objects.filter(email=username).first()
            
            if user:
                
                self.user_cache = authenticate(self.request, username=user.username, password=password)
            else:
                self.user_cache = None

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data



    
#マイページ→プロフィール設定編集画面
class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 全体に適用
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'custom-input'})
            
        # 自己紹介
        self.fields['bio'].widget.attrs.update({'rows': 5}) 
         # リンクを追加
        self.fields['link'].widget.attrs.update({'style': 'height: 40px;'})
        
    class Meta:
        model = Profile
        fields = ['image', 'nickname', 'bio', 'link']
        
#マイページ→メールアドレス変更画面
class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email'] 
        labels = {'email': '新しいメールアドレス'}
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'custom-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['email'].initial = ''
        
        
#マイページ→パスワード変更画面
class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = "現在のパスワード"
        self.fields['new_password1'].label = "新しいパスワード"
        self.fields['new_password2'].label = "新しいパスワード（確認用）"
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'custom-input'})
