from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'valid_from', 'valid_to', 'is_active', 'used_count', 'max_uses']
    list_filter = ['is_active']
    search_fields = ['code']
    list_editable = ['is_active']
