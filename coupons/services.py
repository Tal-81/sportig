"""Coupon service logic."""

from .models import Coupon


class CouponService:
    @staticmethod
    def apply_coupon(code, order_subtotal):
        """
        Validate and calculate discount for a coupon code.
        Returns (discount_amount, message).
        """
        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return 0, 'Invalid coupon code.'

        if not coupon.is_valid:
            return 0, 'This coupon is expired or no longer valid.'

        if order_subtotal < coupon.min_order_amount:
            return 0, f'Minimum order amount of {coupon.min_order_amount} kr required.'

        discount = (order_subtotal * coupon.discount_percent) / 100
        return discount, f'Coupon applied! {coupon.discount_percent}% off.'
