from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from .forms import ProfileForm, SignupForm


# --- マイページ用の処理 ---
@login_required
def mypage_view(request):
    
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
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
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # 1. フォームの内容からユーザーを作成（まだDBには保存しない）
            user = form.save(commit=False)
            # 2. パスワードを暗号化してセット
            user.set_password(form.cleaned_data['password'])
            # 3. DBに保存
            user.save()
            
            # 4. 登録後、そのままログインさせる
            login(request, user)
            
            # 5. マイページへリダイレクト
            return redirect('choco_palette:mypage')
    else:
        # GETのときは空のフォームを表示
        form = SignupForm()
    
    return render(request, 'choco_palette/auth/signup.html', {'form': form})

# --- パスワード再設定画面の表示 ---
def password_reset_view(request):
    """
    パスワード再設定画面を表示する
    """
    return render(request, 'choco_palette/auth/password_reset.html')