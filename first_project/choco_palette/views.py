from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from .forms import ProfileForm

# --- マイページ用の処理 ---
@login_required
def mypage_view(request):
    profile = Profile.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # ユーザー名をUserモデルに反映
            user = request.user
            user.username = form.cleaned_data['username']
            user.save()
            # プロフィールを保存
            form.save()
            return redirect('choco_palette:mypage')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'choco_palette/auth/mypage.html', {'profile': profile, 'form': form})

# --- ログイン用の処理 ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('choco_palette:mypage')
    else:
        form = AuthenticationForm()
    return render(request, 'choco_palette/auth/login.html', {'form': form})

# --- 新規登録用の処理 ---
def signup_view(request):
    return render(request, 'choco_palette/auth/signup.html')