from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'variant_info', 'unit_price', 'quantity', 'line_total']

    def line_total(self, obj):
        return f"{obj.line_total} kr"
    line_total.short_description = 'Line Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'shipping_email', 'user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'stripe_session_id']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'stripe_session_id')
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_first_name', 'shipping_last_name', 'shipping_email',
                'shipping_phone', 'shipping_street', 'shipping_building',
                'shipping_postal_code', 'shipping_city', 'shipping_country'
            )
        }),
        ('Pricing', {
            'fields': ('subtotal', 'shipping_fee', 'discount_amount', 'coupon_code', 'total')
        }),
        ('Meta', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
