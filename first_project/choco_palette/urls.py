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
    
    
    path('test_design/', views.test_design_view, name='test_design'),
    
]
    
