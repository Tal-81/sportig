from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),
    path('recently-viewed/', views.RecentlyViewedView.as_view(), name='recently_viewed'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
    path('api/<int:product_id>/variants/', views.GetVariantSizesView.as_view(), name='get_variants'),
]
