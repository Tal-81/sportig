import stripe
import json
import logging

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction

from orders.models import Order
from products.models import Product
from cart.services import CartService

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class StripeCheckoutView(View):
    """Create Stripe Checkout session and redirect to Stripe."""

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.payment_status == 'completed':
            return redirect('orders:detail', order_number=order.order_number)

        # Build line items for Stripe
        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'sek',
                    'product_data': {
                        'name': item.product_name,
                        'description': item.variant_info or None,
                    },
                    'unit_amount': int(item.unit_price * 100),  # Convert to öre
                },
                'quantity': item.quantity,
            })

        # Add shipping as a line item
        if order.shipping_fee > 0:
            line_items.append({
                'price_data': {
                    'currency': 'sek',
                    'product_data': {'name': 'Shipping (3-5 business days)'},
                    'unit_amount': int(order.shipping_fee * 100),
                },
                'quantity': 1,
            })

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=request.build_absolute_uri(
                    f'/payments/success/?order={order.order_number}'
                ),
                cancel_url=request.build_absolute_uri(
                    f'/payments/cancel/?order={order.order_number}'
                ),
                customer_email=order.shipping_email,
                metadata={
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                },
                # Apply coupon discount if any
                discounts=[{'coupon': _create_stripe_coupon(order.discount_amount)}]
                if order.discount_amount > 0 else [],
            )

            # Save session ID to order
            order.stripe_session_id = session.id
            order.save(update_fields=['stripe_session_id'])

            return redirect(session.url, code=303)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error for order {order.order_number}: {e}")
            return render(request, 'payments/error.html', {
                'message': 'Payment processing error. Please try again.',
                'order': order,
            })


def _create_stripe_coupon(discount_amount):
    """Create a one-time Stripe coupon for a discount amount."""
    try:
        coupon = stripe.Coupon.create(
            amount_off=int(discount_amount * 100),
            currency='sek',
            duration='once',
        )
        return coupon.id
    except stripe.error.StripeError:
        return None


class PaymentSuccessView(View):
    """Handle successful payment redirect from Stripe."""

    def get(self, request):
        order_number = request.GET.get('order')
        if not order_number:
            return redirect('core:home')

        order = get_object_or_404(Order, order_number=order_number)

        # Verify payment via session (security check)
        if order.stripe_session_id:
            try:
                session = stripe.checkout.Session.retrieve(order.stripe_session_id)
                if session.payment_status == 'paid' and order.payment_status != 'completed':
                    _fulfill_order(order)
            except stripe.error.StripeError:
                pass

        # Clear cart and coupon after successful purchase
        if request.user.is_authenticated and order.user == request.user:
            CartService.clear_cart(request)
            request.session.pop('coupon_code', None)

        return render(request, 'payments/success.html', {
            'order': order,
            'page_title': 'Payment Successful',
        })


class PaymentCancelView(View):
    """Handle cancelled payment."""

    def get(self, request):
        order_number = request.GET.get('order')
        order = None
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number, user=request.user)
            except Order.DoesNotExist:
                pass

        return render(request, 'payments/cancel.html', {
            'order': order,
            'page_title': 'Payment Cancelled',
        })


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks for payment verification."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid webhook payload")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid webhook signature")
        return HttpResponse(status=400)

    # Handle checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        if session.payment_status == 'paid':
            order_id = session.metadata.get('order_id')
            try:
                order = Order.objects.get(id=order_id)
                _fulfill_order(order)
            except Order.DoesNotExist:
                logger.error(f"Order {order_id} not found in webhook")

    elif event['type'] == 'payment_intent.payment_failed':
        session = event['data']['object']
        order_id = session.metadata.get('order_id')
        if order_id:
            try:
                Order.objects.filter(id=order_id).update(payment_status='failed')
            except Order.DoesNotExist:
                pass

    return HttpResponse(status=200)


@transaction.atomic
def _fulfill_order(order):
    """Fulfill order: update status, reduce stock, update product sales count."""
    if order.payment_status == 'completed':
        return  # Already fulfilled

    order.payment_status = 'completed'
    order.status = 'paid'
    order.save(update_fields=['payment_status', 'status'])

    # Reduce stock and update sales count
    for item in order.items.select_related('product', 'variant'):
        if item.variant:
            item.variant.__class__.objects.filter(pk=item.variant.pk).update(
                stock_quantity=item.variant.stock_quantity - item.quantity
            )
        elif item.product:
            item.product.__class__.objects.filter(pk=item.product.pk).update(
                stock_quantity=item.product.stock_quantity - item.quantity,
                sales_count=item.product.sales_count + item.quantity,
            )

    logger.info(f"Order {order.order_number} fulfilled successfully.")
