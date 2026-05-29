def wishlist_context(request):
    if request.user.is_authenticated:
        from .models import WishlistItem
        wishlist_ids = list(WishlistItem.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True))
        return {
            'wishlist_product_ids': wishlist_ids,
            'wishlist_count': len(wishlist_ids),
        }
    return {'wishlist_product_ids': [], 'wishlist_count': 0}
