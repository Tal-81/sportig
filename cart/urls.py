from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.AddToCartView.as_view(), name='add'),
    path('remove/<str:item_id>/', views.RemoveFromCartView.as_view(), name='remove'),
    path('update/<str:item_id>/', views.UpdateCartView.as_view(), name='update'),
    path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply_coupon'),
]
