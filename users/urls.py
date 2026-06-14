from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path(
        'profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/change-password/',
         views.ChangePasswordView.as_view(), name='change_password'),
    path('profile/delete/',
         views.DeleteAccountView.as_view(), name='delete_account'),

    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset.html',
        email_template_name='emails/password_reset_email.html',
        subject_template_name='emails/password_reset_subject.txt',
        success_url='/users/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
          template_name='users/password_reset_confirm.html',
          success_url='/users/password-reset/complete/'
         ), name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
          template_name='users/password_reset_complete.html'
         ), name='password_reset_complete'),
]
