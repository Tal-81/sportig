from django.conf import settings
from products.models import Category


def site_context(request):
    """Add global context to all templates."""
    return {
        'CURRENCY_SYMBOL': settings.CURRENCY_SYMBOL,
        'SHIPPING_COST': settings.SHIPPING_COST,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        'all_categories': Category.objects.filter(is_active=True),
        'session_expired': request.session.pop('session_expired', False),
    }
