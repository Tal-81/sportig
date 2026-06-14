from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse

from .models import WishlistItem
from products.models import Product


@method_decorator(login_required, name='dispatch')
class WishlistView(View):
    template_name = 'wishlist/wishlist.html'

    def get(self, request):
        items = WishlistItem.objects.filter(
            user=request.user
        ).select_related('product__category', 'product__brand')
        return render(request, self.template_name, {
            'wishlist_items': items,
            'page_title': 'My Wishlist',
        })


@method_decorator(login_required, name='dispatch')
class ToggleWishlistView(View):
    """ add product if not exists, remove it if exists """
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        existing = WishlistItem.objects.filter(
            user=request.user, product=product
        ).first()

        if existing:
            existing.delete()
            in_wishlist = False
        else:
            WishlistItem.objects.create(user=request.user, product=product)
            in_wishlist = True

        count = WishlistItem.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'in_wishlist': in_wishlist,
            'count': count,
        })


@method_decorator(login_required, name='dispatch')
class RemoveFromWishlistView(View):
    """
    remove one item from wishlist by its ID — calls button (Remove) in the card
    """

    def post(self, request, item_id):
        item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
        item.delete()
        count = WishlistItem.objects.filter(user=request.user).count()
        return JsonResponse({'success': True, 'count': count})


@method_decorator(login_required, name='dispatch')
class ClearWishlistView(View):
    """  clear all items from wishlist."""

    def post(self, request):
        deleted, _ = WishlistItem.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True, 'count': 0, 'deleted': deleted})
