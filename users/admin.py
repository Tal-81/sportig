from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('avatar', 'phone_number')
        }),
        ('Address', {
            'fields': ('street_name', 'building_number', 'postal_code', 'city', 'country')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile Info', {
            'fields': ('email', 'first_name', 'last_name', 'phone_number')
        }),
    )
