from django.contrib import admin
from .models import (
                        Category,
                        Brand,
                        Product,
                        ProductImage,
                        ProductVariant,
                        HeroBanner,
                        NewsletterSubscription
                    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
                   'name', 'category', 'brand', 'price', 'discount_price',
                   'stock_quantity', 'is_featured', 'is_active', 'sales_count',
                   'created_at'
                   ]
    list_filter = ['is_active', 'is_featured', 'category', 'brand', 'gender']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'is_active', 'price', 'stock_quantity']
    inlines = [ProductImageInline, ProductVariantInline]
    readonly_fields = [
                      'views_count', 'sales_count', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Info', {
            'fields': (
                'name', 'slug', 'description', 'category', 'brand', 'gender')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'is_featured', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': (
                'views_count', 'sales_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order']
    list_editable = ['is_active', 'order']


@admin.register(NewsletterSubscription)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active']
