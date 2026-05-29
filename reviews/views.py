from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from .models import Review
from products.models import Product
from orders.models import OrderItem


@method_decorator(login_required, name='dispatch')
class AddReviewView(View):
    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug, is_active=True)

        # Verify buyer
        is_buyer = OrderItem.objects.filter(
            order__user=request.user,
            product=product,
            order__status='delivered'
        ).exists()

        if not is_buyer:
            return redirect('products:detail', slug=product_slug)

        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()

        if not comment:
            return redirect('products:detail', slug=product_slug)

        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={'rating': rating, 'comment': comment}
        )

        return redirect('products:detail', slug=product_slug)


@method_decorator(login_required, name='dispatch')
class DeleteReviewView(View):
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        product_slug = review.product.slug
        review.delete()
        return redirect('products:detail', slug=product_slug)
