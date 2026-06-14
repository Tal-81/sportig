from django.db import models
from django.conf import settings
from products.models import Product, ProductVariant


class Cart(models.Model):
    """Database cart for authenticated users."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.email}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.select_related(
            'product',
            'variant'))

    @property
    def shipping_cost(self):
        return settings.SHIPPING_COST if self.items.exists() else 0

    @property
    def total(self):
        return self.subtotal + self.shipping_cost


class CartItem(models.Model):
    """Individual item in a cart."""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
        )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def unit_price(self):
        return self.product.current_price

    @property
    def line_total(self):
        return self.unit_price * self.quantity
