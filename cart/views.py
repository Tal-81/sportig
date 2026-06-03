from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.conf import settings

from .services import CartService


class CartView(View):
    template_name = 'cart/cart.html'

    def get(self, request):
        cart = CartService.get_cart(request)

        coupon_discount = 0
        coupon_code     = request.session.get('coupon_code')
        if coupon_code:
            from coupons.services import CouponService
            discount, _ = CouponService.apply_coupon(coupon_code, cart['subtotal'])
            if discount:
                coupon_discount = discount

        return render(request, self.template_name, {
            'cart':               cart,
            'coupon_discount':    coupon_discount,
            'coupon_code':        coupon_code,
            'total_after_discount': cart['total'] - coupon_discount,
            'page_title':         'Shopping Cart',
        })


class AddToCartView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity   = max(1, int(request.POST.get('quantity', 1)))
        variant_id = request.POST.get('variant_id') or None

        success, message = CartService.add_item(request, product_id, quantity, variant_id)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = CartService.get_cart(request)
            return JsonResponse({
                'success':     success,
                'message':     message,
                'total_items': cart['total_items'],
            })

        return redirect('cart:cart')


class RemoveFromCartView(View):
    def post(self, request, item_id):
        CartService.remove_item(request, item_id)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = CartService.get_cart(request)
            return JsonResponse({
                'success':     True,
                'total_items': cart['total_items'],
                'subtotal':    float(cart['subtotal']),
                'shipping':    float(cart['shipping']),
                'total':       float(cart['total']),
            })

        return redirect('cart:cart')


class UpdateCartView(View):
    def post(self, request, item_id):
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        # ── Prevent quantity from going below 1 ──────────
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': 'Minimum quantity is 1.',
            })

        # ── Check available stock ────────────────────
        stock_check = _check_stock(request, item_id, quantity)
        if not stock_check['ok']:
            return JsonResponse({
                'success': False,
                'message': stock_check['message'],
            })

        success, message = CartService.update_quantity(request, item_id, quantity)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = CartService.get_cart(request)

            # Calculate line_total for the updated item
            line_total = _get_line_total(cart, item_id)

            return JsonResponse({
                'success':     success,
                'message':     message,
                'total_items': cart['total_items'],
                'subtotal':    float(cart['subtotal']),
                'shipping':    float(cart['shipping']),
                'total':       float(cart['total']),
                'line_total':  float(line_total),
            })

        return redirect('cart:cart')


class ApplyCouponView(View):
    def post(self, request):
        coupon_code = request.POST.get('coupon_code', '').strip().upper()

        if coupon_code:
            cart = CartService.get_cart(request)
            from coupons.services import CouponService
            discount, message = CouponService.apply_coupon(coupon_code, cart['subtotal'])
            if discount:
                request.session['coupon_code'] = coupon_code
            else:
                request.session.pop('coupon_code', None)
        else:
            request.session.pop('coupon_code', None)

        request.session.modified = True
        return redirect('cart:cart')


# ── Helpers ────────────────────────────────────────────────

def _check_stock(request, item_id, requested_qty):
    """
    Check the available stock for the item.
    Takes into account the variant (color/size) if it exists.
    """
    try:
        if request.user.is_authenticated:
            from cart.models import CartItem
            item = CartItem.objects.select_related(
                'product', 'variant'
            ).get(id=item_id, cart__user=request.user)

            if item.variant:
                available = item.variant.stock_quantity
                label = f"{item.variant.color} / {item.variant.size}"
            else:
                available = item.product.stock_quantity
                label = item.product.name

        else:
            # Session cart
            cart = request.session.get('cart', {})
            item_data = cart.get(str(item_id))
            if not item_data:
                return {'ok': True}  # Item not found — let the service handle it

            from products.models import Product, ProductVariant
            product = Product.objects.get(id=item_data['product_id'])

            if item_data.get('variant_id'):
                variant   = ProductVariant.objects.get(id=item_data['variant_id'])
                available = variant.stock_quantity
                label     = f"{variant.color} / {variant.size}"
            else:
                available = product.stock_quantity
                label     = product.name

        if requested_qty > available:
            return {
                'ok':      False,
                'message': f'Only {available} item(s) available for {label}.',
            }

        return {'ok': True}

    except Exception:
        # In case of any unexpected error — leave it to the service
        return {'ok': True}


def _get_line_total(cart, item_id):
    """Get the line_total for the item from the updated cart data."""
    str_id = str(item_id)
    for item in cart.get('items', []):
        if str(item.get('id', '')) == str_id:
            return item.get('line_total', 0)
    return 0
