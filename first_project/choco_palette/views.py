# --- Django標準ライブラリ ---
from django.shortcuts import render, redirect, get_object_or_404  # 画面表示・リダイレクト・404制御
from django.contrib import messages                                # 完了通知などのトーストメッセージ用
from django.urls import reverse_lazy                               # URL名からパスを逆引きするツール
from django.db.models import Q                                     # 複雑なクエリ（公開/非公開）の条件分岐用
from django.core.paginator import Paginator                       # 投稿リストのページ分割機能
from django.http import JsonResponse                               # Ajax通信のレスポンス用
from django.views.decorators.csrf import csrf_exempt              # CSRFチェック除外用（必要に応じて）

# --- Django認証関連 ---
from django.contrib.auth import authenticate, login                # ユーザー認証とログイン処理の実行
from django.contrib.auth.decorators import login_required          # ログイン必須ページを守るための機能
from django.contrib.auth.forms import AuthenticationForm           # 標準のログイン用フォーム
from django.contrib.auth.views import PasswordResetConfirmView     # パスワードリセット後の確認用画面

# --- 自作のモデルとフォーム ---
from .models import Profile, Post                                  # プロフィールと投稿のデータ構造
from .forms import ProfileForm, SignupForm, PostForm, LoginForm    # 各画面の入力フォーム定義（LoginFormを追加）

# --- マイページ用の処理 ---
@login_required
def mypage_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid(): # プロフィールを保存
           form.save()
        return redirect('choco_palette:mypage')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'choco_palette/auth/mypage.html', {'profile': profile, 'form': form})

# --- ログイン用の処理 ---
def login_view(request):
    if request.method == 'POST':
        # AuthenticationForm の代わりに LoginForm を使う
        form = LoginForm(request, data=request.POST) 
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('choco_palette:post_list')
    else:
        form = LoginForm() # ここも LoginForm にする
    return render(request, 'choco_palette/auth/login.html', {'form': form})

# --- 新規登録用の処理 ---
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)    # 1. フォームの内容からユーザーを作成
            user.set_password(form.cleaned_data['password']) # 2. パスワードを暗号化してセット
            user.save()   # 3. DBに保存
            login(request, user)# 4. 登録後、そのままログインさせる
            return redirect('choco_palette:mypage')  # 5. マイページへリダイレクト
    else:
        form = SignupForm()   # GETのときは空のフォームを表示
    return render(request, 'choco_palette/auth/signup.html', {'form': form})

# --- 新パスワード設定トースト通知 ---
class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'choco_palette/auth/password_reset_confirm.html'
    success_url = reverse_lazy('login')  # ログイン画面へ遷移
    def form_valid(self, form): # 成功時にトースト通知を追加
        messages.success(self.request, "新しいパスワードを設定しました！")
        return super().form_valid(form)
   
def test_design_view(request):
    from django.contrib.auth.forms import SetPasswordForm
    form = SetPasswordForm(user=None)# 確認用
    return render(request, 'choco_palette/auth/password_reset_confirm.html', {'form': form})

# --- テイスティング投稿の処理 ---
@login_required
def post_create(request):
    if request.method == 'POST':    # 送られてきたデータと画像を受け取る
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False) # 1. フォームの内容から投稿を作成
            post.user = request.user # 2. ユーザーを紐付け
            post.save() # 3. DBに保存
            form.save_m2m() #4. 多対多保存
            messages.success(request, '投稿完了しました！') # 5. 投稿完了後にトースト通知を表示
            return redirect('choco_palette:post_list') #5.一覧画面へリダイレクト
    else:
        form = PostForm() # GETのときは空のフォームを表示
    return render(request, 'choco_palette/post/post_create.html', {'form': form})

# --- ホーム画面（投稿一覧表示） ---
def post_list(request):
    if request.user.is_authenticated: 
        posts_all = Post.objects.filter(
            Q(status=1) | Q(user=request.user, status=2)
        ).order_by('-created_at')
    else:
        posts_all = Post.objects.filter(status=1).order_by('-created_at')
    paginator = Paginator(posts_all, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'choco_palette/post/post_list.html', {'page_obj': page_obj})

# --- テイスティング投稿詳細画面 ---
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'choco_palette/post/post_detail.html', {'post': post})

# --- お気に入り保存処理 ---
@login_required
def post_like(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=pk)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# --- 編集処理（枠組み） ---
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'choco_palette/post/post_edit.html', {'post': post})

# --- 削除処理 ---
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.user:
        post.delete()
        messages.success(request, '投稿を削除しました。')
    return redirect('choco_palette:post_list')