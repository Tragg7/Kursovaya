from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('panel/', views.admin_panel_view, name='admin_panel'),
    path('courier/', views.courier_panel_view, name='courier_panel'),
    path('cart/update/<str:item_name>/', views.update_quantity_view, name='update_quantity'),
    path('cart/checkout/', views.checkout_view, name='checkout'),
    path('cart/clear/', views.clear_cart_view, name='clear_cart'),
    path('cart/add/', views.add_to_cart_view, name='add_to_cart'),
]