from django.urls import path
from . import views

urlpatterns = [
    path('asset_quick_search', views.asset_quick_search, name='appStockTrade-asset_quick_search'),
    path('asset_advanced_search', views.asset_advanced_search, name='appStockTrade-asset_advanced_search'),
    path('stock_details/', views.stock_details, name='appStockTrade-stock_details'),
]
