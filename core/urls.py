from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('newsletter/signup/', views.NewsletterSignupView.as_view(), name='newsletter_signup'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
]
