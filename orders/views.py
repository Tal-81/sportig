from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction

from .models import Order, OrderItem
from cart.services import CartService
from .forms import CheckoutForm


@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    template_name = 'orders/checkout.html'

    def get(self, request):
        cart = CartService.get_cart(request)
        if not cart['items']:
            return redirect('cart:cart')

        # Pre-fill form with user address
        initial = {}
        user = request.user
        if user.has_complete_address():
            initial = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone_number,
                'street': user.street_name,
                'building': user.building_number,
                'postal_code': user.postal_code,
                'city': user.city,
                'country': user.country,
            }

        coupon_discount = 0
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            from coupons.services import CouponService
            # ←  return 3 values
            discount, message, status = CouponService.apply_coupon(
                coupon_code, cart['subtotal']
            )
            if discount:
                coupon_discount = discount

        form = CheckoutForm(initial=initial)
        return render(request, self.template_name, {
            'cart': cart,
            'form': form,
            'coupon_discount': coupon_discount,
            'coupon_code': coupon_code,
            'total_after_discount': cart['total'] - coupon_discount,
            'page_title': 'Checkout',
        })

    def post(self, request):
        cart = CartService.get_cart(request)
        if not cart['items']:
            return redirect('cart:cart')

        form = CheckoutForm(request.POST)
        if form.is_valid():
            coupon_discount = 0
            coupon_code = request.session.get('coupon_code')
            if coupon_code:
                from coupons.services import CouponService
                # ← return 3 values
                discount, message, status = CouponService.apply_coupon(
                    coupon_code, cart['subtotal']
                )
                if discount:
                    coupon_discount = discount

            total = cart['total'] - coupon_discount

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    shipping_first_name=form.cleaned_data['first_name'],
                    shipping_last_name=form.cleaned_data['last_name'],
                    shipping_email=form.cleaned_data['email'],
                    shipping_phone=form.cleaned_data.get('phone', ''),
                    shipping_street=form.cleaned_data['street'],
                    shipping_building=form.cleaned_data.get('building', ''),
                    shipping_postal_code=form.cleaned_data['postal_code'],
                    shipping_city=form.cleaned_data['city'],
                    shipping_country=form.cleaned_data['country'],
                    subtotal=cart['subtotal'],
                    shipping_fee=cart['shipping'],
                    discount_amount=coupon_discount,
                    coupon_code=coupon_code or '',
                    total=total,
                    notes=form.cleaned_data.get('notes', ''),
                )

                for item in cart['items']:
                    variant_info = ''
                    if item['variant']:
                        variant_info = (
                            f"{item['variant'].color} / "
                            f"{item['variant'].size}"
                        )

                    sku = (
                        item['variant'].sku
                        if item['variant']
                        else ''
                    )

                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        variant=item['variant'],
                        product_name=item['product'].name,
                        product_sku=sku,
                        variant_info=variant_info,
                        unit_price=item['unit_price'],
                        quantity=item['quantity'],
                    )

            request.session['pending_order_id'] = order.id
            return redirect('payments:checkout', order_id=order.id)

        # إعادة عرض النموذج مع الأخطاء
        coupon_discount = 0
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            from coupons.services import CouponService
            discount, message, status = CouponService.apply_coupon(
                coupon_code, cart['subtotal']
            )
            if discount:
                coupon_discount = discount

        return render(request, self.template_name, {
            'cart': cart,
            'form': form,
            'coupon_discount': coupon_discount,
            'coupon_code': coupon_code,
            'total_after_discount': cart['total'] - coupon_discount,
            'page_title': 'Checkout',
        })


@method_decorator(login_required, name='dispatch')
class OrderListView(View):
    template_name = 'orders/order_list.html'

    def get(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).prefetch_related('items').order_by('-created_at')
        return render(request, self.template_name, {
            'orders': orders,
            'page_title': 'My Orders',
        })


@method_decorator(login_required, name='dispatch')
class OrderDetailView(View):
    template_name = 'orders/order_detail.html'

    def get(self, request, order_number):
        order = get_object_or_404(
            Order.objects.prefetch_related(
                'items__product', 'items__variant'
            ),
            order_number=order_number,
            user=request.user,
        )
        return render(request, self.template_name, {
            'order': order,
            'page_title': f'Order #{order.order_number}',
        })


@method_decorator(login_required, name='dispatch')
class DownloadInvoiceView(View):
    def get(self, request, order_number):
        from django.contrib import messages
        order = get_object_or_404(
            Order.objects.prefetch_related('items__product'),
            order_number=order_number,
            user=request.user,
        )
        if order.payment_status != 'completed':
            messages.error(
                request, 'Invoice only available for paid orders.'
            )
            return redirect('orders:detail', order_number=order_number)

        from services.pdf_service import generate_invoice_pdf
        return generate_invoice_pdf(order)
