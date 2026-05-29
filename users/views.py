"""
Views for user authentication and profile management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.db import transaction

from .models import User
from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm,
    CustomPasswordChangeForm, DeleteAccountForm
)
from orders.models import Order


class RegisterView(View):
    template_name = 'users/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        form = UserRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to Sportig, {user.first_name}! Your account has been created.')
            return redirect('core:home')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'users/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:home')
        form = UserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Merge guest cart after login
            _merge_guest_cart(request, user)
            next_url = request.GET.get('next', 'core:home')
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect(next_url)
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('core:home')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'users/profile.html'

    def get(self, request):
        orders = Order.objects.filter(user=request.user).select_related(
        ).prefetch_related('items__product').order_by('-created_at')[:5]
        return render(request, self.template_name, {
            'orders': orders,
            'page_title': 'My Profile'
        })


@method_decorator(login_required, name='dispatch')
class EditProfileView(View):
    template_name = 'users/edit_profile.html'

    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    template_name = 'users/change_password.html'

    def get(self, request):
        form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('users:profile')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class DeleteAccountView(View):
    template_name = 'users/delete_account.html'

    def get(self, request):
        if not request.user.can_delete_account():
            return redirect('users:profile')
        form = DeleteAccountForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if not request.user.can_delete_account():
            return redirect('users:profile')
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = authenticate(request, email=request.user.email, password=password)
            if user:
                logout(request)
                with transaction.atomic():
                    user.delete()
                return redirect('core:home')
            else:
                form.add_error('password', 'Incorrect password.')
        return render(request, self.template_name, {'form': form})


def _merge_guest_cart(request, user):
    """Merge session-based guest cart into database cart after login."""
    from cart.services import CartService
    CartService.merge_guest_cart(request, user)
