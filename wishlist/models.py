"""Wishlist: model, view, context_processor, URL."""

from django.db import models
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.shortcuts import render

from products.models import Product


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
