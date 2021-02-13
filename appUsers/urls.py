from django.urls import path
from . import views

urlpatterns = [
    path('login_page/', views.login_page, name='appUsers-login_page'),
    path('register/', views.register, name='appUsers-register'),
    path('logout/', views.logout_user, name='appUsers-logout'),
    path('', views.home, name='appUsers-home'),
]