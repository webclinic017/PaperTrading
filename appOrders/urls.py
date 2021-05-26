from django.urls import path
from . import views

urlpatterns = [
    path('place_buy_order', views.place_buy_order, name='appOrders-place_buy_order'),
    path('place_sell_order', views.place_sell_order, name='appOrders-place_sell_order'),
    path('submit_buy_order', views.submit_buy_order, name='appOrders-submit_buy_order'),
    path('view_all_orders', views.view_all_orders, name='appOrders-view_all_orders'),
    path('view_all_positions', views.view_all_positions, name='appOrders-view_all_positions'),
]
