from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.WishlistView.as_view(), name='wishlist'),
    path('toggle/<int:product_id>/', views.ToggleWishlistView.as_view(), name='toggle'),
    path('remove/<int:item_id>/', views.RemoveFromWishlistView.as_view(), name='remove'),
    path('clear/', views.ClearWishlistView.as_view(), name='clear'),   # ← جديد
]
