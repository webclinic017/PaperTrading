from django.urls import path
from . import views

urlpatterns = [
    path('stock_search', views.stock_search, name='appStockTrade-stock_search'),
    path('stock_details/', views.stock_details, name='appStockTrade-stock_details'),
]