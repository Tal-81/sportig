from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from .models import WishlistItem
from products.models import Product


@method_decorator(login_required, name='dispatch')
class WishlistView(View):
    template_name = 'wishlist/wishlist.html'

    def get(self, request):
        items = WishlistItem.objects.filter(user=request.user).select_related('product__category')
        return render(request, self.template_name, {
            'wishlist_items': items,
            'page_title': 'My Wishlist',
        })


@method_decorator(login_required, name='dispatch')
class ToggleWishlistView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)
        item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)

        if not created:
            item.delete()
            in_wishlist = False
        else:
            in_wishlist = True

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            count = WishlistItem.objects.filter(user=request.user).count()
            return JsonResponse({'in_wishlist': in_wishlist, 'count': count})

        return redirect(request.META.get('HTTP_REFERER', 'wishlist:wishlist'))


@method_decorator(login_required, name='dispatch')
class RemoveFromWishlistView(View):
    def post(self, request, item_id):
        WishlistItem.objects.filter(id=item_id, user=request.user).delete()
        return redirect('wishlist:wishlist')
