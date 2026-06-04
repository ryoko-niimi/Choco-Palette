from django.urls import path
from . import views 

app_name = 'choco_palette' 

urlpatterns = [
    
    path('login/', views.login_view, name='login'), 
    path('signup/', views.signup_view, name='signup'),
    path('mypage/', views.mypage_view, name='mypage'),
    
]