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
from django.contrib.auth.models import User 

# --- 自作のモデルとフォーム ---
from .models import Profile, Post, PostPhoto, TasteTag, AromaTag
from .forms import ProfileForm, SignupForm, PostForm, LoginForm
from django.core.paginator import Paginator

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
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('choco_palette:mypage')
    else:
        form = SignupForm()
    return render(request, 'choco_palette/auth/signup.html', {'form': form})

# --- 新パスワード設定トースト通知 ---
class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'choco_palette/auth/password_reset_confirm.html'
    success_url = reverse_lazy('login')
    def form_valid(self, form):
        messages.success(self.request, "新しいパスワードを設定しました！")
        return super().form_valid(form)
   
def test_design_view(request):
    from django.contrib.auth.forms import SetPasswordForm
    form = SetPasswordForm(user=None)
    return render(request, 'choco_palette/auth/password_reset_confirm.html', {'form': form})

# --- テイスティング投稿の処理 ---
def post_create(request):
    if request.method == 'POST':    
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if not request.user.is_authenticated:
                post.status = 1
                post.user = None
            else:
                post.user = request.user
            post.save()
            form.save_m2m()
            images = request.FILES.getlist('images')
            for image in images:
                PostPhoto.objects.create(post=post, image=image)
            messages.success(request, '投稿完了しました！')
            return redirect('choco_palette:post_list')
    else:
        form = PostForm()
    return render(request, 'choco_palette/post/post_create.html', {
        'form': form,
        'all_taste_tags': TasteTag.objects.all(),
        'all_aroma_tags': AromaTag.objects.all(),
    })

# --- ホーム画面（投稿一覧表示） ---
def post_list(request):
    if request.user.is_authenticated: 
        posts = Post.objects.filter(Q(status=1) | Q(user=request.user, status=2))
    else:
        posts = Post.objects.filter(status=1)
    
    query = request.GET.get('q')
    min_cacao = request.GET.get('min_cacao')
    max_cacao = request.GET.get('max_cacao')
    taste_ids = request.GET.getlist('taste')
    aroma_ids = request.GET.getlist('aroma')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status_filter = request.GET.getlist('status')
    favorite_rates = request.GET.getlist('rate')

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
        elif 'private' in status_filter and request.user.is_authenticated:
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

# --- 編集処理 ---
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.user != request.user:
        messages.error(request, '他人の投稿は編集できません。')
        return redirect('choco_palette:post_list')
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            updated_post.tasting_date = post.tasting_date 
            updated_post.save()
            form.save_m2m()  
            images = request.FILES.getlist('images')
            for image in images:
                PostPhoto.objects.create(post=updated_post, image=image)
            messages.success(request, '投稿を更新しました！')
            return redirect('choco_palette:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'choco_palette/post/post_create.html', {
        'form': form, 
        'post': post, 
        'all_taste_tags': TasteTag.objects.all(), 
        'all_aroma_tags': AromaTag.objects.all(),
    })

# --- 下書き一覧 ---
@login_required
def draft_list(request):
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

# --- 下書き投稿の削除処理 ---
@login_required 
@require_POST
def draft_delete(request):
    if request.method == 'POST':
        post_ids = request.POST.getlist('post_ids')
        if post_ids:
            Post.objects.filter(id__in=post_ids).delete()
            messages.success(request, '削除しました！')
    return redirect('choco_palette:draft_list')

# --- ユーザープロフィール表示画面 ---
def user_profile(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    
    #  投稿のフィルタリング（公開投稿を基本とする）
    all_posts = Post.objects.filter(user=target_user, status=1).order_by('-created_at')
    
    # 自分のプロフィールなら非公開も追加（フィルタリング後に結合）
    if request.user.is_authenticated and request.user == target_user:
        private_posts = Post.objects.filter(user=target_user, status=2)
        all_posts = (all_posts | private_posts).order_by('-created_at')
    
    # 5件ずつ表示する設定（ページネーション）
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'target_user': target_user,
        'page_obj': page_obj,  
    }
    
    return render(request, 'choco_palette/user_profile.html', context)

# --- マイページ画面---
def mypage(request):
    return render(request, 'choco_palette/mypage.html')