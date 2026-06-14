from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path(
        'checkout/<int:order_id>/',
        views.StripeCheckoutView.as_view(),
        name='checkout'),
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
]
