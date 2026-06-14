from django.utils import timezone
from .models import Coupon


class CouponService:

    @staticmethod
    def apply_coupon(code, order_subtotal):
        """
        Validate and calculate discount for a coupon code.
        Returns (discount_amount, message, status).
        status: 'success' | 'expired' | 'invalid' | 'min_amount' | 'inactive'
        """
        code = code.strip().upper()

        if not code:
            return 0, 'Please enter a coupon code.', 'invalid'

        #   Is coupon code valid?
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return (
                0,
                f'Coupon "{code}" does not exist. '
                f'Please check the code and try again.',
                'invalid'
            )

        #   Is coupon active?
        if not coupon.is_active:
            return 0, f'Coupon "{code}" is no longer active.', 'inactive'

        now = timezone.now()

        #   Is coupon valid from?
        if now < coupon.valid_from:
            start_date = coupon.valid_from.strftime("%d %b %Y")
            return (
                0,
                f'Coupon "{code}" is not valid yet. '
                f'It starts on {start_date}.',
                'invalid'
            )

        #   Has coupon expired?
        if now > coupon.valid_to:
            expired_date = coupon.valid_to.strftime("%d %b %Y")
            return 0, f'Coupon "{code}" expired on {expired_date}.', 'expired'

        #   Has coupon reached its usage limit?
        if coupon.used_count >= coupon.max_uses:
            return (
                0,
                f'Coupon "{code}" has reached its usage limit.', 'inactive'
                )

        #   Is order subtotal enough for this coupon?
        if order_subtotal < coupon.min_order_amount:
            return (
                0,
                f'Minimum order amount for this coupon is '
                f'{coupon.min_order_amount:,.0f} kr. '
                f'Your subtotal is {order_subtotal:,.0f} kr.',
                'min_amount'
            )

        # ── If everything is valid ──────────────────────────────────
        discount = (order_subtotal * coupon.discount_percent) / 100
        return (
            discount,
            f'Coupon "{code}" applied! You get {coupon.discount_percent}% '
            f'off — saving {discount:,.0f} kr.',
            'success'
        )
