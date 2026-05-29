"""
Cart views: display, add, remove, update operations.
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.conf import settings

from .services import CartService


class CartView(View):
    template_name = 'cart/cart.html'

    def get(self, request):
        cart = CartService.get_cart(request)

        # Apply coupon discount if any
        coupon_discount = 0
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            from coupons.services import CouponService
            discount, message = CouponService.apply_coupon(coupon_code, cart['subtotal'])
            if discount:
                coupon_discount = discount

        total_after_discount = cart['total'] - coupon_discount

        return render(request, self.template_name, {
            'cart': cart,
            'coupon_discount': coupon_discount,
            'coupon_code': coupon_code,
            'total_after_discount': total_after_discount,
            'page_title': 'Shopping Cart',
        })


class AddToCartView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        variant_id = request.POST.get('variant_id') or None

        success, message = CartService.add_item(request, product_id, quantity, variant_id)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = CartService.get_cart(request)
            return JsonResponse({
                'success': success,
                'message': message,
                'total_items': cart['total_items'],
            })

        return redirect('cart:cart')


class RemoveFromCartView(View):
    def post(self, request, item_id):
        CartService.remove_item(request, item_id)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = CartService.get_cart(request)
            return JsonResponse({
                'success': True,
                'total_items': cart['total_items'],
                'subtotal': float(cart['subtotal']),
                'total': float(cart['total']),
            })

        return redirect('cart:cart')


class UpdateCartView(View):
    def post(self, request, item_id):
        quantity = int(request.POST.get('quantity', 1))
        success, message = CartService.update_quantity(request, item_id, quantity)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = CartService.get_cart(request)
            return JsonResponse({
                'success': success,
                'message': message,
                'total_items': cart['total_items'],
                'subtotal': float(cart['subtotal']),
                'shipping': float(cart['shipping']),
                'total': float(cart['total']),
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
                request.session.modified = True
            else:
                request.session.pop('coupon_code', None)
                request.session.modified = True
        else:
            request.session.pop('coupon_code', None)
            request.session.modified = True

        return redirect('cart:cart')
