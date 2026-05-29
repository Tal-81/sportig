from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('my-orders/', views.OrderListView.as_view(), name='list'),
    path('<str:order_number>/', views.OrderDetailView.as_view(), name='detail'),
    path('<str:order_number>/invoice/', views.DownloadInvoiceView.as_view(), name='invoice'),
]
