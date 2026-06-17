from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views


app_name = 'choco_palette' 

urlpatterns = [
    path('login/', views.login_view, name='login'), 
    path('signup/', views.signup_view, name='signup'),
    path('mypage/', views.mypage_view, name='mypage'),
    #パスワードの再設定画面
    path('password_reset/', 
     auth_views.PasswordResetView.as_view(
         template_name='choco_palette/auth/password_reset.html',
         email_template_name='choco_palette/auth/password_reset_email.html', 
         success_url='/password_reset/done/'
     ), 
     name='password_reset'),
    
    #メール送信後の完了画面
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='choco_palette/auth/password_reset_done.html'), 
         name='password_reset_done'),
    
    # 新パスワードの設定画面
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='choco_palette/auth/password_reset_confirm.html'), 
         name='password_reset_confirm'),
 
 
    # 投稿・テイスティング記録
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('post/', views.post_list, name='post_list'),
    
    # テスト用
    path('test_design/', views.test_design_view, name='test_design'),
 
    #テイスティング投稿詳細画面
    #テイスティング投稿詳細画面
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    
]
   
 
   
