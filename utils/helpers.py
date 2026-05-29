"""
General utility helpers used across the application.
"""

import random
import string
from django.utils.text import slugify


def generate_unique_slug(model_class, name, slug_field='slug'):
    """Generate a unique slug for a model instance."""
    base_slug = slugify(name)
    slug = base_slug
    counter = 1

    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


def generate_order_reference(length=8):
    """Generate a random uppercase alphanumeric order reference."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def format_price_sek(amount):
    """Format a price in Swedish Krona."""
    return f"{amount:,.0f} kr".replace(',', ' ')
