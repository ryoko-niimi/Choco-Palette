from django import forms
from .models import Profile, Post, TasteTag, AromaTag
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone


        
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
        
        widgets = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # すべてのフィールドにクラスを追加し、PasswordInputを明示的に指定
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    # 重複メールアドレスチェック
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # 既存のユーザーに同じメールアドレスが存在するかチェック
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('このメールアドレスは既に登録されています')
            
        return email
    
    # パスワードのルールチェック（半角英数字含む８文字以上）
    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # 1. 8文字以上かチェック
        if password and len(password) < 8:
            raise forms.ValidationError("パスワードは8文字以上で入力してください。")
            
        # 2. Django標準のパスワードバリデーション（英数字チェック等）
        try:
            validate_password(password)
        except ValidationError as e:
            raise forms.ValidationError("パスワードには英数字を組み合わせてください。")
            
        return password
    

    # パスワードの一致チェック
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
            'status': forms.RadioSelect(choices=[
                (Post.STATUS_PUBLIC, "公開"),
                (Post.STATUS_PRIVATE, "非公開"),
            ]),
            'cacao_percentage': forms.NumberInput(attrs={'placeholder': '不明な場合は空欄OK', 'class': 'form-control'}),
            'tasting_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'},format='%Y-%m-%d'), 
            'tasting_comment': forms.Textarea(attrs={'placeholder': '', 'rows': 4, 'class': 'form-control'}),
            'private_memo': forms.Textarea(attrs={'placeholder': '自分用メモ（非公開）', 'rows': 4, 'class': 'form-control'}),
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
        self.fields['tasting_date'].label = f'テイスティング日{badge}'
        
        # 3. その他（バッジなしの項目）のラベルを日本語に設定
        self.fields['cacao_percentage'].label = 'カカオ含有率'
        self.fields['favorite_rate'].label = 'お気に入り度'
        self.fields['tasting_comment'].label = 'テイスティングコメント'
        self.fields['private_memo'].label = 'プライベートメモ'
        self.fields['taste_tags'].label = '味タグ'
        self.fields['aroma_tags'].label = '香りタグ'
        
        # 4. 必須設定
        self.fields['chocolate_name'].required = True
        self.fields['brand_name'].required = True
        self.fields['status'].required = True
        self.fields['tasting_date'].required = True
        
        # 5. 空欄OK設定
        self.fields['cacao_percentage'].required = False
        self.fields['tasting_comment'].required = False
        self.fields['private_memo'].required = False
        self.fields['favorite_rate'].required = False

        # 6. カスタムエラーメッセージの設定 
        self.fields['chocolate_name'].error_messages['required'] = '商品名を入力してください'
        self.fields['brand_name'].error_messages['required'] = 'ブランド名を入力してください'
        self.fields['status'].error_messages['required'] = '公開・非公開を選択してください'
        self.fields['tasting_date'].error_messages['required'] = 'テイスティング日を選択してください'
        
        # 7. 日付を取得して未来の日付は選択できなくする
        today_str = timezone.localdate().strftime('%Y-%m-%d')
        self.fields['tasting_date'].widget.attrs['max'] = today_str
        
    def clean_tasting_date(self):
        tasting_date = self.cleaned_data.get('tasting_date')
        if tasting_date and tasting_date > timezone.localdate():
            raise forms.ValidationError('未来の日付は選択できません。')
        return tasting_date

       


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
    class Meta:
        model = Profile
        fields = ['image', 'nickname', 'bio', 'introduction', 'link']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 全体に適用
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'custom-input'})
            
        # 自己紹介
        self.fields['bio'].widget.attrs.update({'rows': 5}) 
        
         # リンクを追加
        self.fields['link'].widget.attrs.update({'style': 'height: 40px;'})
        self.fields['link'].widget.attrs.update({
            'style': 'height: 40px;',
            'placeholder': 'SNSなどのURLを入力してください'
        })
        

        
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
            
    # パスワードのルールチェック（半角英数字含む８文字以上）
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        # 1. 8文字以上かチェック
        if password and len(password) < 8:
            raise ValidationError("パスワードは8文字以上で入力してください。")
            
        # 2. Django標準のバリデーションチェック
        try:
            validate_password(password)
        except ValidationError as e:
            raise ValidationError("パスワードには英数字を組み合わせてください。")
            
        return password
    
