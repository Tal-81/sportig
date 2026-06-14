"""
Product models: Category, Brand, Product, ProductVariant, ProductImage.
"""

from django.db import models
from django.utils.text import slugify
from django.db.models import Avg, Count
from cloudinary.models import CloudinaryField


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('sportswear', 'Sportswear'),
        ('sneakers', 'Sneakers'),
        ('gym-equipment', 'Gym Equipment'),
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('baseball', 'Baseball'),
        ('golf', 'Golf'),
        ('rugby', 'Rugby'),
        ('running', 'Running'),
        ('other', 'Other Sports'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = CloudinaryField(
        'category_image',
        blank=True, null=True,
        folder='categories/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:category', kwargs={'slug': self.slug})


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    logo = CloudinaryField(
        'brand_logo',
        blank=True,
        null=True,
        folder='brands/')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    GENDER_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
        ('unisex', 'Unisex'),
    ]

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=300)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True)
    main_image = CloudinaryField('product_image', folder='products/')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='products')
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products')
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='unisex')
    stock_quantity = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'gender']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:detail', kwargs={'slug': self.slug})

    @property
    def current_price(self):
        """Return discount price if available, else regular price."""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def average_rating(self):
        result = self.reviews.aggregate(avg=Avg('rating'))
        return round(result['avg'] or 0, 1)

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0 or self.variants.filter(
            stock_quantity__gt=0).exists()

    def get_main_image_url(self):
        if self.main_image:
            return self.main_image.url
        return '/static/images/no-image.png'


class ProductImage(models.Model):
    """Additional gallery images for a product."""
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = CloudinaryField('product_gallery', folder='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"


class ProductVariant(models.Model):
    """Product variants for size and color combinations."""
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
        ('45', '45'),
        ('46', '46'),
        ('47', '47'),
        ('48', '48'),
        ('ONE SIZE', 'One Size'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants'
        )
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    color_hex = models.CharField(max_length=7, blank=True, default='#000000')
    stock_quantity = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True)

    class Meta:
        unique_together = ['product', 'size', 'color']
        ordering = ['size', 'color']

    def __str__(self):
        return f"{self.product.name} - {self.color} / {self.size}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.id}-{slugify(self.color)}-{self.size}"
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class HeroBanner(models.Model):
    """Hero slider banners for the homepage."""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    button_text = models.CharField(max_length=50, default='Shop Now')
    button_url = models.CharField(max_length=255, default='/')
    image = CloudinaryField('hero_banner', folder='banners/')
    image_mobile = CloudinaryField(
        'hero_banner_mobile', folder='banners/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email
