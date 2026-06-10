from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from .forms import ProfileForm, SignupForm
from django.shortcuts import render

from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib import messages
from django.urls import reverse_lazy

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

# --- 新パスワード設定トースト通知 ---
class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'choco_palette/auth/password_reset_confirm.html'
    success_url = reverse_lazy('login')  # ログイン画面へ遷移

    def form_valid(self, form):
        # 成功時にトースト通知を追加
        messages.success(self.request, "新しいパスワードを設定しました！")
        return super().form_valid(form)
    
def test_design_view(request):
    from django.contrib.auth.forms import SetPasswordForm
    # 確認用
    form = SetPasswordForm(user=None)
    return render(request, 'choco_palette/auth/password_reset_confirm.html', {'form': form})