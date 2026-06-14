"""
Cart service: handles both guest (session) and user (database) cart operations.
"""

from django.conf import settings
from django.db import transaction

from .models import Cart, CartItem
from products.models import Product, ProductVariant


class CartService:
    """Unified cart service for session and database carts."""

    @staticmethod
    def get_cart(request):
        """Return cart data dict regardless of user state."""
        if request.user.is_authenticated:
            return CartService._get_db_cart(request.user)
        return CartService._get_session_cart(request)

    @staticmethod
    def _get_db_cart(user):
        """Build cart data from database cart."""
        cart, _ = Cart.objects.get_or_create(user=user)
        items = cart.items.select_related('product', 'variant').all()
        cart_items = []
        for item in items:
            cart_items.append({
                'id': item.id,
                'product': item.product,
                'variant': item.variant,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'line_total': item.line_total,
            })
        subtotal = sum(i['line_total'] for i in cart_items)
        shipping = settings.SHIPPING_COST if cart_items else 0
        return {
            'items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': subtotal + shipping,
            'total_items': sum(i['quantity'] for i in cart_items),
        }

    @staticmethod
    def _get_session_cart(request):
        """Build cart data from session."""
        session_cart = request.session.get('cart', {})
        cart_items = []
        subtotal = 0
        total_items = 0

        for key, item_data in session_cart.items():
            try:
                product = Product.objects.get(
                    id=item_data['product_id'], is_active=True
                )
                variant = None
                if item_data.get('variant_id'):
                    variant = ProductVariant.objects.get(
                        id=item_data['variant_id']
                    )
                quantity = item_data['quantity']
                unit_price = product.current_price
                line_total = unit_price * quantity
                subtotal += line_total
                total_items += quantity
                cart_items.append({
                    'id': key,
                    'product': product,
                    'variant': variant,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'line_total': line_total,
                })
            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                continue

        shipping = settings.SHIPPING_COST if cart_items else 0
        return {
            'items': cart_items,
            'subtotal': subtotal,
            'shipping': shipping,
            'total': subtotal + shipping,
            'total_items': total_items,
        }

    @staticmethod
    def add_item(request, product_id, quantity=1, variant_id=None):
        """Add item to cart."""
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return False, 'Product not found.'

        variant = None
        if variant_id:
            try:
                variant = ProductVariant.objects.get(
                    id=variant_id, product=product
                )
            except ProductVariant.DoesNotExist:
                return False, 'Variant not found.'

        # Stock check
        stock = (
            variant.stock_quantity if variant else product.stock_quantity
        )
        if quantity > stock:
            return False, f'Only {stock} items available in stock.'

        if request.user.is_authenticated:
            return CartService._add_to_db_cart(
                request.user, product, variant, quantity
            )
        return CartService._add_to_session_cart(
            request, product, variant, quantity
        )

    @staticmethod
    @transaction.atomic
    def _add_to_db_cart(user, product, variant, quantity):
        cart, _ = Cart.objects.get_or_create(user=user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant,
            defaults={'quantity': 0}
        )
        new_qty = item.quantity + quantity
        stock = (
            variant.stock_quantity if variant else product.stock_quantity
        )
        if new_qty > stock:
            return False, f'Cannot add more. Only {stock} available.'
        item.quantity = new_qty
        item.save()
        return True, 'Item added to cart.'

    @staticmethod
    def _add_to_session_cart(request, product, variant, quantity):
        cart = request.session.get('cart', {})
        key = f"{product.id}_{variant.id if variant else 'none'}"
        if key in cart:
            new_qty = cart[key]['quantity'] + quantity
            stock = (
                variant.stock_quantity if variant else product.stock_quantity
            )
            if new_qty > stock:
                return False, f'Cannot add more. Only {stock} available.'
            cart[key]['quantity'] = new_qty
        else:
            cart[key] = {
                'product_id': product.id,
                'variant_id': variant.id if variant else None,
                'quantity': quantity,
            }
        request.session['cart'] = cart
        request.session.modified = True
        return True, 'Item added to cart.'

    @staticmethod
    def remove_item(request, item_id):
        """Remove item from cart."""
        if request.user.is_authenticated:
            CartItem.objects.filter(
                id=item_id, cart__user=request.user
            ).delete()
        else:
            cart = request.session.get('cart', {})
            cart.pop(str(item_id), None)
            request.session['cart'] = cart
            request.session.modified = True

    @staticmethod
    def update_quantity(request, item_id, quantity):
        """Update item quantity."""
        if quantity <= 0:
            CartService.remove_item(request, item_id)
            return True, 'Item removed.'

        if request.user.is_authenticated:
            try:
                item = CartItem.objects.get(
                    id=item_id, cart__user=request.user
                )
                stock = (
                    item.variant.stock_quantity
                    if item.variant
                    else item.product.stock_quantity
                )
                if quantity > stock:
                    return False, f'Only {stock} available.'
                item.quantity = quantity
                item.save()
                return True, 'Quantity updated.'
            except CartItem.DoesNotExist:
                return False, 'Item not found.'
        else:
            cart = request.session.get('cart', {})
            if str(item_id) in cart:
                cart[str(item_id)]['quantity'] = quantity
                request.session['cart'] = cart
                request.session.modified = True
                return True, 'Quantity updated.'
            return False, 'Item not found.'

    @staticmethod
    def clear_cart(request):
        """Clear all items from cart."""
        if request.user.is_authenticated:
            Cart.objects.filter(user=request.user).delete()
        else:
            request.session['cart'] = {}
            request.session.modified = True

    @staticmethod
    def merge_guest_cart(request, user):
        """Merge session cart into database cart after user login."""
        session_cart = request.session.get('cart', {})
        if not session_cart:
            return

        db_cart, _ = Cart.objects.get_or_create(user=user)

        for key, item_data in session_cart.items():
            try:
                product = Product.objects.get(id=item_data['product_id'])
                variant = None
                if item_data.get('variant_id'):
                    variant = ProductVariant.objects.get(
                        id=item_data['variant_id']
                    )

                item, created = CartItem.objects.get_or_create(
                    cart=db_cart, product=product, variant=variant,
                    defaults={'quantity': 0}
                )
                item.quantity += item_data['quantity']
                item.save()
            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                continue

        # Clear session cart
        request.session['cart'] = {}
        request.session.modified = True
