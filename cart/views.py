from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from .services import CartService


class CartView(View):
    template_name = 'cart/cart.html'

    def get(self, request):
        cart = CartService.get_cart(request)

        coupon_discount = 0
        coupon_code     = request.session.get('coupon_code')
        coupon_message  = None
        coupon_status   = None

        if coupon_code:
            from coupons.services import CouponService
            discount, message, status = CouponService.apply_coupon(
                coupon_code, cart['subtotal']
            )
            if discount:
                coupon_discount = discount
            else:
                #  coupon is invalid — remove it from the session
                request.session.pop('coupon_code', None)
                request.session.modified = True
                coupon_code = None

        return render(request, self.template_name, {
            'cart':                 cart,
            'coupon_discount':      coupon_discount,
            'coupon_code':          coupon_code,
            'total_after_discount': cart['total'] - coupon_discount,
            'page_title':           'Shopping Cart',
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

        if quantity < 1:
            return JsonResponse({'success': False, 'message': 'Minimum quantity is 1.'})

        #  verify stock before updating quantity
        stock_check = _check_stock(request, item_id, quantity)
        if not stock_check['ok']:
            return JsonResponse({'success': False, 'message': stock_check['message']})

        success, message = CartService.update_quantity(request, item_id, quantity)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart       = CartService.get_cart(request)
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
    """
    handle both applying and removing coupons based on 
    the presence of coupon_code in POST data.
    return JSON with clear toast messages for each case.
    """

    def post(self, request):
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        is_ajax     = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # ── Remove coupon (empty field or Remove button) ──────────
        if not coupon_code:
            removed = request.session.pop('coupon_code', None)
            request.session.modified = True

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'status':  'removed',
                    'message': 'Coupon removed.' if removed else '',
                    'discount': 0,
                })
            return redirect('cart:cart')

        # ── apply coupon ──────────────────────────────────
        cart = CartService.get_cart(request)

        from coupons.services import CouponService
        discount, message, status = CouponService.apply_coupon(
            coupon_code, cart['subtotal']
        )

        if status == 'success':
            request.session['coupon_code'] = coupon_code
        else:
            request.session.pop('coupon_code', None)
        request.session.modified = True

        if is_ajax:
            cart_updated = CartService.get_cart(request)
            return JsonResponse({
                'success':   status == 'success',
                'status':    status,
                'message':   message,
                'discount':  float(discount),
                'subtotal':  float(cart_updated['subtotal']),
                'shipping':  float(cart_updated['shipping']),
                'total':     float(cart_updated['total']),
                'coupon_code': coupon_code if status == 'success' else '',
            })

        return redirect('cart:cart')


# ── helpers ──────────────────────────────────────────────

def _check_stock(request, item_id, requested_qty):
    try:
        if request.user.is_authenticated:
            from cart.models import CartItem
            item = CartItem.objects.select_related(
                'product', 'variant'
            ).get(id=item_id, cart__user=request.user)
            if item.variant:
                available = item.variant.stock_quantity
                label     = f"{item.variant.color} / {item.variant.size}"
            else:
                available = item.product.stock_quantity
                label     = item.product.name
        else:
            cart_session = request.session.get('cart', {})
            item_data    = cart_session.get(str(item_id))
            if not item_data:
                return {'ok': True}
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
        return {'ok': True}


def _get_line_total(cart, item_id):
    for item in cart.get('items', []):
        if str(item.get('id', '')) == str(item_id):
            return item.get('line_total', 0)
    return 0
