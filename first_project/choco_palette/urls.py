from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

app_name = 'choco_palette' 

urlpatterns = [
     
    #ポートフォリオ
    path('', views.portfolio_view, name='home'),
    
    # ホーム画面（一覧画面をホームとする）
    path('posts/', views.post_list, name='post_list') ,

    # 認証関連
    path('login/', views.login_view, name='login'), 
    path('signup/', views.signup_view, name='signup'),
    
    
    # パスワードの再設定画面
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='choco_palette/auth/password_reset.html',
             email_template_name='choco_palette/auth/password_reset_email.html', 
             subject='【Choco Palette】パスワード再設定のご案内', 
             success_url='/password_reset/done/'
         ), 
         name='password_reset'),
    
    # メール送信後の完了画面
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='choco_palette/auth/password_reset_done.html'), 
         name='password_reset_done'),
    
    # 新パスワードの設定画面
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='choco_palette/auth/password_reset_confirm.html',
             success_url='/reset/done/'  
         ), 
         name='password_reset_confirm'),
    
    # 新パスワード変更完了画面
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='choco_palette/auth/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    

    # 投稿・テイスティング記録
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('post/', views.post_list, name='post_list'),
    
    # テスト用
    path('test_design/', views.test_design_view, name='test_design'),

    # テイスティング投稿詳細画面
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'), # お気に入りボタン
    
    # 検索・絞り込み画面
    path('search/', views.search_view, name='search'),
    
    #投稿済・下書き一覧からのテイスティング編集画面で画像「削除」処理
    path('post/photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    
    #投稿済・下書き一覧からのテイスティング編集画面で画像「並べ替え」処理
    path('post/photo/reorder/', views.reorder_photos, name='reorder_photos'),
   
    
    
    
    #下書き一覧表示画面
    path('drafts/', views.draft_list, name='draft_list'),
    path('drafts/delete/', views.draft_delete, name='draft_delete'),
    
    #ユーザープロフィール表示画面
    path('user_profile/<int:user_id>/', views.user_profile, name='user_profile'),
    path('posts/delete/', views.post_delete, name='post_delete'),
    
   
   #マイページ画面
   path('mypage/', views.mypage, name='mypage'),
   #プロフィール編集画面
   path('profile_edit/',views.profile_edit, name='profile_edit'),
   #メールアドレス変更画面
   path('email_change/', views.email_change, name='email_change'),
   #パスワード変更画面
   path('password_change/', views.password_change, name='password_change'),
   #お気に入り一覧画面
   path('favorites/', views.favorites_list, name='favorites_list'),
   # お気に入り投稿削除
   path('mypage/favorites/remove/', views.remove_favorites, name='favorites_list_remove'),
   #ログアウト処理
   path('logout/', views.custom_logout, name='logout'),
   
   
    
]