from .services import CartService

def cart_context(request):
    """Add cart data to all templates."""
    try:
        cart = CartService.get_cart(request)
        return {'cart_total_items': cart['total_items']}
    except Exception:
        return {'cart_total_items': 0}
