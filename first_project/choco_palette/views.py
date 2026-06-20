# --- Django標準ライブラリ ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# --- Django認証関連 ---
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetConfirmView

# --- 自作のモデルとフォーム ---
from .models import Profile, Post, PostPhoto, TasteTag, AromaTag
from .forms import ProfileForm, SignupForm, PostForm, LoginForm



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
        form = LoginForm(request, data=request.POST) 
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('choco_palette:post_list')
    else:
        form = LoginForm() 
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
    if request.method == 'POST':    
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False) # 1. フォームの内容から投稿を作成
            post.user = request.user       # 2. ユーザーを紐付け
            post.save()                    # 3. DBに保存
            form.save_m2m()                # 4. 多対多保存
            
            # 画像をまとめて保存（追加部分）
            images = request.FILES.getlist('images')
            for image in images:
                PostPhoto.objects.create(post=post, image=image)

            messages.success(request, '投稿完了しました！') # 5. 投稿完了後にトースト通知を表示
            return redirect('choco_palette:post_list') # 5. 一覧画面へリダイレクト
    else:
        form = PostForm() # GETのときは空のフォームを表示する
    return render(request, 'choco_palette/post/post_create.html', {'form': form})

# --- ホーム画面（投稿一覧表示） ---
def post_list(request):
    # 基本のクエリ：ログイン状態に応じて公開/非公開を切り替える
    if request.user.is_authenticated: 
        posts = Post.objects.filter(
            Q(status=1) | Q(user=request.user, status=2)
        )
    else:
        posts = Post.objects.filter(status=1)
    
    # --- フォームから送られてきたデータを読み取る ---
    query = request.GET.get('q')
    min_cacao = request.GET.get('min_cacao')
    max_cacao = request.GET.get('max_cacao')
    taste_ids = request.GET.getlist('taste')  # チェックボックスはgetlistで受け取る
    aroma_ids = request.GET.getlist('aroma')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # --- 検索処理の追加・修正 ---
    status_filter = request.GET.getlist('status')
    favorite_rates = request.GET.getlist('rate')

    # 条件に合うものを絞り込む
    if query:
        posts = posts.filter(Q(chocolate_name__icontains=query) | Q(brand_name__icontains=query))
    if min_cacao:
        posts = posts.filter(cacao_percentage__gte=min_cacao)
    if max_cacao:
        posts = posts.filter(cacao_percentage__lte=max_cacao)
    if taste_ids:
        posts = posts.filter(taste_tags__id__in=taste_ids).distinct()
    if aroma_ids:
        posts = posts.filter(aroma_tags__id__in=aroma_ids).distinct()
    if start_date:
        posts = posts.filter(tasting_date__gte=start_date)
    if end_date:
        posts = posts.filter(tasting_date__lte=end_date)
    
    if status_filter:
        if 'public' in status_filter and 'private' in status_filter:
            pass 
        elif 'public' in status_filter:
            posts = posts.filter(status=1)
        elif 'private' in status_filter:
            posts = posts.filter(status=2, user=request.user)
    
    if favorite_rates:
        posts = posts.filter(favorite_rate__in=favorite_rates)
    
    posts = posts.order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'choco_palette/post/post_list.html', {'page_obj': page_obj})

# --- 検索画面の表示 ---
def search_view(request):
    context = {
        'taste_tags': TasteTag.objects.all(),
        'aroma_tags': AromaTag.objects.all(),
    }
    return render(request, 'choco_palette/post/search.html', context)

# --- テイスティング投稿詳細画面 ---
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(id=request.user.id).exists()
    
    return render(request, 'choco_palette/post/post_detail.html', {
        'post': post,
        'is_liked': is_liked,
    })

# --- お気に入り ---
@login_required
@require_POST
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked = True
    return JsonResponse({'status': 'success', 'is_liked': is_liked})

# --- 編集処理（投稿・編集共通のpost_create.htmlを使用） ---
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # 自分の投稿のみ編集
    if post.user != request.user:
        messages.error(request, '他人の投稿は編集できません。')
        return redirect('choco_palette:post_list')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            # 1. フォームの保存（ただし日付だけは編集不可）
            updated_post = form.save(commit=False)
            updated_post.tasting_date = post.tasting_date  
            updated_post.save()
            form.save_m2m()  

            # 2. 写真の追加保存処理
            images = request.FILES.getlist('images')
            for image in images:
                PostPhoto.objects.create(post=updated_post, image=image)
            
            messages.success(request, '投稿を更新しました！')
            return redirect('choco_palette:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    # 修正後：post_create.html を使い回す
    return render(request, 'choco_palette/post/post_create.html',{
        'form': form, 'post': post,'all_taste_tags': TasteTag.objects.all(),'all_aroma_tags': AromaTag.objects.all(),})

# --- 下書き一覧 ---
@login_required
def draft_list(request):
    # ログインユーザーの非公開投稿のみ取得
    drafts = Post.objects.filter(user=request.user, status=2).order_by('-created_at')
    return render(request, 'choco_palette/post/draft_list.html', {'drafts': drafts})



# --- 投稿削除処理 ---
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.user:
        post.delete()
        messages.success(request, '投稿を削除しました。')
    return redirect('choco_palette:post_list')
    
# --- 投稿画像削除処理 ---
@login_required
@require_POST  
def delete_photo(request, photo_id):
    photo = get_object_or_404(PostPhoto, id=photo_id, post__user=request.user)
    photo.delete()  
    return JsonResponse({'status': 'success'})