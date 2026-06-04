from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'nickname', 'introduction']
        labels = {
            'image': 'プロフィール画像',
            'nickname': 'ニックネーム',
            'introduction': '自己紹介文',
        }