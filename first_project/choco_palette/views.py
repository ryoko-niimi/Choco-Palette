# --- Django標準ライブラリ ---
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
# --- Django標準ライブラリ ---
from django.views.decorators.http import require_POST
# --- 認証関連 ---
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.models import User 
from django.contrib.auth import update_session_auth_hash
from .forms import MyPasswordChangeForm

# --- 投稿 ---
from .models import Profile, Post, PostPhoto, TasteTag, AromaTag
from django.contrib.auth.forms import UserChangeForm
from .forms import ProfileForm, SignupForm, PostForm, EmailLoginForm, EmailChangeForm  

# --- 投稿画像並べ替え    ---
from django.http import JsonResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import PostPhoto

# 【追加】画像の一覧取得・並び替え配慮用のインポート
from django.db.models import Prefetch

# --- ポートフォリオ ---
def portfolio_view(request):
    return render(request, 'choco_palette/portfolio.html')

# --- ログイン用の処理 ---
def login_view(request):
    if request.method == 'POST':
        # 【修正】メールアドレスログイン用のフォーム（EmailLoginForm）を使用
        form = EmailLoginForm(request, data=request.POST) 
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('choco_palette:post_list')
    else:
        # 【修正】画面を開いた時も EmailLoginForm を表示
        form = EmailLoginForm() 
    return render(request, 'choco_palette/auth/login.html', {'form': form})


# --- 新規アカウント登録用の処理 ---
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        
        if form.is_valid():    
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            image = request.FILES.get('image')
            Profile.objects.create(user=user, nickname=user.username,image=image)
            
            return redirect('choco_palette:login')
            
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
    back_url = request.META.get(
        'HTTP_REFERER',
        reverse_lazy('choco_palette:post_list')
    )

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)

        # 枚数制限チェック
        files = request.FILES.getlist('images')

        if len(files) > 10:
            messages.error(request, '写真は最大10枚までです。')

            return render(request, 'choco_palette/post/post_create.html', {
                'form': form,
                'back_url': back_url,
                'all_taste_tags': TasteTag.objects.all(),
                'all_aroma_tags': AromaTag.objects.all(),
            })

        if form.is_valid():
            post = form.save(commit=False)

            # ログインしていれば投稿者を保存
            post.user = (
                None
                if not request.user.is_authenticated
                else request.user
            )

            # 下書き保存か、通常投稿かを判定
            action = request.POST.get('action')

            if action == 'save':
                post.status = 0 # 下書き
                message = '下書きを保存しました！'
                redirect_url = 'choco_palette:draft_list'
            else:
                # フォームで選択されたstatusをそのまま使う
                post.status = form.cleaned_data.get('status', 1) 
                message = '投稿完了しました！'
                redirect_url = 'choco_palette:post_list'

            # 投稿本体を保存
            post.save()

            # 味タグ・香りタグなどのManyToMany項目を保存
            form.save_m2m()

            # --- 修正版の画像保存ロジック ---
            
            # 1. 送られてきた並び順JSONを取り出す
            photo_order_json = request.POST.get('photo_order', '[]')
            photo_order = json.loads(photo_order_json)
            
            # 2. 新規画像を順番に保存
            # ここではシンプルに、HTML側の「new」の数に合わせてファイルを割り当てます
            new_files = [f for f in files] 
            new_file_index = 0
            
            for index, item in enumerate(photo_order):
                if item == 'new':
                    if new_file_index < len(new_files):
                        PostPhoto.objects.create(
                            post=post,
                            image=new_files[new_file_index],
                            sort_order=index # ここに正しい順番が入る！
                        )
                        new_file_index += 1
                elif item.startswith('existing:'):
                    # 編集画面で既存画像を並び替えた場合の処理
                    photo_id = item.split(':')[1]
                    try:
                        photo = PostPhoto.objects.get(id=photo_id, post=post)
                        photo.sort_order = index
                        photo.save()
                    except PostPhoto.DoesNotExist:
                        pass

            # 保存完了メッセージ
            messages.success(request, message)

            # 下書き一覧または投稿一覧へ移動
            return redirect(redirect_url)

    else:
        form = PostForm()

    return render(request, 'choco_palette/post/post_create.html', {
        'form': form,
        'back_url': back_url,
        'all_taste_tags': TasteTag.objects.all(),
        'all_aroma_tags': AromaTag.objects.all(),
    })
    

# --- ホーム画面（投稿一覧表示） ---
def post_list(request):
    
    posts = Post.objects.exclude(status=0).prefetch_related(
        Prefetch('photos', queryset=PostPhoto.objects.order_by('sort_order'))
    )
    
    if request.user.is_authenticated:
        
        posts = posts.filter(Q(status=1) | (Q(status=2) & Q(user=request.user)))
    else:
        
        posts = posts.filter(status=1)

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
    
    post = get_object_or_404(
        Post.objects.prefetch_related(
            Prefetch('photos', queryset=PostPhoto.objects.order_by('sort_order'), to_attr='ordered_photos')
        ), 
        pk=pk
    )
    is_liked = False
    is_owner = False
    
    if request.user.is_authenticated:
        is_liked = post.likes.filter(id=request.user.id).exists()
        
        if post.user == request.user:
            is_owner = True
    
    back_url = request.GET.get('from', 'home')
    
    return render(request, 'choco_palette/post/post_detail.html', {
        'post': post,
        'is_liked': is_liked,
        'is_owner': is_owner, 
        'back_url': back_url, 
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

    # 他のユーザーの投稿は編集できないようにする
    if post.user != request.user:
        messages.error(request, '他人の投稿は編集できません。')
        return redirect('choco_palette:post_list')

    back_url = request.META.get(
        'HTTP_REFERER',
        reverse_lazy('choco_palette:post_list')
    )

    if request.method == 'POST':
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )
    
        files = request.FILES.getlist('images')

        # 枚数制限チェック
        # 既存画像の枚数＋今回追加する画像の枚数が10枚を超えないか確認
        current_count = PostPhoto.objects.filter(post=post).count()

        if current_count + len(files) > 10:
            messages.error(
                request,
                f'写真は最大10枚までです。（現在{current_count}枚登録済み）'
            )

            return render(
                request,
                'choco_palette/post/post_create.html',
                {
                    'form': form,
                    'post': post,
                    'back_url': back_url,
                    'existing_photos': PostPhoto.objects.filter(
                        post=post
                    ).order_by('sort_order', 'id'),
                    'all_taste_tags': TasteTag.objects.all(),
                    'all_aroma_tags': AromaTag.objects.all(),
                }
            )

        if form.is_valid():
            updated_post = form.save(commit=False)

            # 下書き保存か、通常投稿かを判定
            action = request.POST.get('action')

            if action == 'save':
                updated_post.status = 0
                msg = '下書きを保存しました！'
                redirect_url = 'choco_palette:draft_list'
            else:
                updated_post.status = 1
                msg = '投稿しました！'
                redirect_url = 'choco_palette:post_list'

            updated_post.save()

            # 味タグ・香りタグなどのManyToMany項目を保存
            form.save_m2m()

            # ----------------------------------------
            # 画像の並び順を保存
            # ----------------------------------------

            photo_order_json = request.POST.get('photo_order', '')

            try:
                if photo_order_json:
                    photo_order = json.loads(photo_order_json)
                else:
                    photo_order = []

                # JSONの内容がリストでなければ、空のリストにする
                if not isinstance(photo_order, list):
                    photo_order = []

            except json.JSONDecodeError:
                # 並び順データを正しく読み取れなかった場合
                photo_order = []

            # この投稿に現在保存されている画像を取得
            existing_photos = list(
                PostPhoto.objects.filter(
                    post=updated_post
                ).order_by('sort_order', 'id')
            )

            existing_photo_map = {
                str(photo.id): photo
                for photo in existing_photos
            }

            # 同じ既存画像を2回保存しないための記録
            used_existing_ids = set()

            # 新規画像を順番に1枚ずつ取り出すための準備
            new_file_iterator = iter(files)

            # 並び順どおりに処理する画像を入れるリスト
            ordered_items = []

            # ----------------------------------------
            # HTMLから送られた順番を読み取る
            # ----------------------------------------
            for order_item in photo_order:

                # 保存済み画像の場合
                if (
                    isinstance(order_item, str)
                    and order_item.startswith('existing:')
                ):
                    photo_id = order_item.split(':', 1)[1]

                    photo = existing_photo_map.get(photo_id)

                    if (
                        photo is not None
                        and photo_id not in used_existing_ids
                    ):
                        ordered_items.append({
                            'type': 'existing',
                            'photo': photo,
                        })

                        used_existing_ids.add(photo_id)

                # 新しく追加した画像の場合
                elif order_item == 'new':
                    try:
                        new_file = next(new_file_iterator)

                        ordered_items.append({
                            'type': 'new',
                            'file': new_file,
                        })

                    except StopIteration:
                        # newの印より実際の画像枚数が少ない場合は何もしない
                        pass

            # ----------------------------------------
            # 並び順データに入っていなかった既存画像を末尾へ追加
            # ----------------------------------------
        
            for photo in existing_photos:
                photo_id = str(photo.id)

                if photo_id not in used_existing_ids:
                    ordered_items.append({
                        'type': 'existing',
                        'photo': photo,
                    })

                    used_existing_ids.add(photo_id)

            # ----------------------------------------
            # 並び順データに入っていなかった新規画像を末尾へ追加
            # ----------------------------------------
            
            for remaining_file in new_file_iterator:
                ordered_items.append({
                    'type': 'new',
                    'file': remaining_file,
                })

            # ----------------------------------------
            # sort_orderの一時変更
            # ----------------------------------------
            
            for temporary_index, photo in enumerate(existing_photos):
                photo.sort_order = 100 + temporary_index
                photo.save(update_fields=['sort_order'])

            # ----------------------------------------
            # 画面上の順番どおりに保存
            # ----------------------------------------
            for sort_index, item in enumerate(ordered_items):

                # 保存済み画像の順番を更新
                if item['type'] == 'existing':
                    photo = item['photo']
                    photo.sort_order = sort_index
                    photo.save(update_fields=['sort_order'])

                # 新規画像を指定された位置へ保存
                elif item['type'] == 'new':
                    PostPhoto.objects.create(
                        post=updated_post,
                        image=item['file'],
                        sort_order=sort_index
                    )

            messages.success(request, msg)
            return redirect(redirect_url)

    else:
        form = PostForm(instance=post)

    # 編集画面を開くときはsort_order順に画像を表示
    # NULL値を避けるためにsort_orderが等しい場合はidでソート
    existing_photos = PostPhoto.objects.filter(
        post=post
    ).order_by('sort_order', 'id')

    return render(
        request,
        'choco_palette/post/post_create.html',
        {
            'form': form,
            'post': post,
            'existing_photos': existing_photos, # このリストが確実に順序通りであること
            'back_url': back_url,
            'all_taste_tags': TasteTag.objects.all(),
            'all_aroma_tags': AromaTag.objects.all(),
        }
    )

# --- 下書き一覧 ---
@login_required
def draft_list(request):
    
    posts = Post.objects.filter(user=request.user, status=0).prefetch_related(
        Prefetch('photos', queryset=PostPhoto.objects.order_by('sort_order'))
    ).order_by('-created_at')
    

    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'choco_palette/post/draft_list.html', {'page_obj': page_obj})

# --- 投稿削除処理 ---
@login_required
def post_delete(request, pk):
    if request.method == 'POST':
        
        post = get_object_or_404(Post, pk=pk, user=request.user)
        post.delete()
        
        
        messages.success(request, '削除しました！')
        
        
        return redirect('choco_palette:post_list')
    
    
    return redirect('choco_palette:post_detail', pk=pk)

# --- 投稿画像削除処理 ---
@login_required
@require_POST  
def delete_photo(request, photo_id):
    photo = get_object_or_404(PostPhoto, id=photo_id, post__user=request.user)
    photo.delete()  
    return JsonResponse({'status': 'success'})

# --- 投稿画像並べ替え処理 ---
@login_required
@require_POST 
def reorder_photos(request):
    import json
    try:
        data = json.loads(request.body)
        photo_ids = data.get('photo_ids', [])
        
        for index, photo_id in enumerate(photo_ids):
        
            photo = get_object_or_404(PostPhoto, id=photo_id, post__user=request.user)
            photo.sort_order = index
            photo.save()
            
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



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

# --- お気に入り投稿、❤の削除処理 ---
@login_required
@require_POST 
def remove_favorites(request):
    post_ids = request.POST.getlist('post_ids')
    if post_ids:
        posts = Post.objects.filter(id__in=post_ids)
        for post in posts:
            post.likes.remove(request.user)
        messages.success(request, 'お気に入りから解除しました！')
    
    return redirect('choco_palette:favorites_list')


# --- ユーザープロフィール表示画面 ---
def user_profile(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST' and request.user == target_user:
        post_ids = request.POST.getlist('post_ids')
        if post_ids:
            # 自分の投稿のみを対象に削除
            Post.objects.filter(id__in=post_ids, user=target_user).delete()
            messages.success(request, '削除しました！')
        # 削除後にリダイレクトすることで、再送信（フォームの二重送信）を防ぐ
        return redirect('choco_palette:user_profile', user_id=user_id)

    # 2. 表示用データの取得
    condition = Q(user=target_user, status=1)
    if request.user.is_authenticated and request.user == target_user:
        condition |= Q(user=target_user, status=2)
    
    all_posts = Post.objects.filter(condition).prefetch_related(
        Prefetch('photos', queryset=PostPhoto.objects.order_by('sort_order'), to_attr='ordered_photos')
    ).order_by('-created_at')
    
    paginator = Paginator(all_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'target_user': target_user, 'page_obj': page_obj}
    return render(request, 'choco_palette/user_profile.html', context)
   


# --- マイページ関連の処理 ---
@login_required
def mypage(request):
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'choco_palette/mypage/mypage.html', {'profile': profile})



# --- マイページ→プロフィール編集画面 ---
@login_required
def profile_edit(request):
    
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    
    if not profile.nickname:
        profile.nickname = request.user.username
        profile.save()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'プロフィールが更新されました')
            return redirect('choco_palette:mypage')
    else:
        
        form = ProfileForm(instance=profile)
    
    return render(request, 'choco_palette/mypage/profile_edit.html', {
        'form': form,
        'profile': profile
    })

# --- マイページ→メールアドレス変更画面 ---
@login_required
def email_change(request):
    # ログインユーザーを取得
    user = request.user
    
    # メールアドレスがDB上で空なら、強制的に仮の値をセットして保存
    if not user.email:
        user.email = "example@example.com"  # 一時的な初期値
        user.save(update_fields=['email'])  # メールアドレスだけを更新保存する
        print("--- メールの空欄を修正しました ---")
    
    print("--- デバッグ: email_change 実行中 ---")
    print(f"メールアドレス: '{user.email}'")
    
    if request.method == 'POST':
        
        form = EmailChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'メールアドレスを変更しました')
            return redirect('choco_palette:mypage')
    else:
        
        form = EmailChangeForm()
    
   
    return render(request, 'choco_palette/mypage/email_change.html', {
        'form': form,
        'user_email': user.email  
    })
    

# --- マイページ→パスワード変更画面---
@login_required
def password_change(request):
    if request.method == 'POST':
        form = MyPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # パスワード変更後にログアウトさせない
            messages.success(request, 'パスワードを変更しました')
            return redirect('choco_palette:mypage')
    else:
        form = MyPasswordChangeForm(request.user)
    
    return render(request, 'choco_palette/mypage/password_change.html', {'form': form})

# --- マイページ→お気に入り一覧画面---
@login_required
def favorites_list(request):
    fav_posts = Post.objects.filter(likes=request.user).prefetch_related(
        Prefetch('photos', queryset=PostPhoto.objects.order_by('sort_order'))
    ).order_by('-created_at')
    
    paginator = Paginator(fav_posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    

    return render(request, 'choco_palette/mypage/favorites.html', {'page_obj': page_obj})


# --- マイページ→ログアウト画面---
@login_required
def custom_logout(request):
    logout(request)
    return redirect('choco_palette:post_list')

