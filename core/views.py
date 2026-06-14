from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse, HttpResponse

from products.models import (Product, Category, HeroBanner,
                             NewsletterSubscription)


class HomeView(View):
    template_name = 'core/home.html'

    def get(self, request):
        banners = HeroBanner.objects.filter(is_active=True).order_by('order')
        featured_products = Product.objects.filter(
            is_featured=True, is_active=True
        ).select_related('category', 'brand')[:8]

        trending_products = Product.objects.filter(
            is_active=True
        ).order_by('-views_count').select_related('category')[:8]

        best_sellers = Product.objects.filter(
            is_active=True
        ).order_by('-sales_count').select_related('category')[:8]

        new_arrivals = Product.objects.filter(
            is_active=True
        ).order_by('-created_at').select_related('category')[:8]

        categories = Category.objects.filter(is_active=True)[:8]

        faqs = [
            {
                'question': 'What is the delivery time?',
                'answer': (
                    'All orders are delivered within 3–5 business days '
                    'across Sweden. International shipping may take longer.'
                )
            },
            {
                'question': 'What is the shipping cost?',
                'answer': (
                    'We offer a flat shipping rate of 100 kr for all orders. '
                    'Free shipping is available during special promotions.'
                )
            },
            {
                'question': 'Can I return or exchange a product?',
                'answer': (
                    'Yes! We offer a 30-day return policy. Items must be in '
                    'their original condition with tags attached. Contact our '
                    'support team to initiate a return.'
                )
            },
            {
                'question': 'How do I track my order?',
                'answer': (
                    'Once your order is shipped, you will receive a '
                    'confirmation email with a tracking number. You can also '
                    'view your order status in your account dashboard.'
                )
            },
            {
                'question': 'Are your products authentic?',
                'answer': (
                    'Absolutely. We only stock genuine products from '
                    'authorized brand suppliers. Every item is 100% authentic '
                    'and comes with original packaging.'
                )
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': (
                    'We accept all major credit and debit cards including '
                    'Visa, Mastercard, and American Express through our '
                    'secure Stripe payment gateway.'
                )
            },
            {
                'question': 'How can I contact customer support?',
                'answer': (
                    'You can reach us through our support ticket system in '
                    'your account, or email us directly. Our team responds '
                    'within 24 hours on business days.'
                )
            },
        ]

        return render(request, self.template_name, {
            'banners': banners,
            'featured_products': featured_products,
            'trending_products': trending_products,
            'best_sellers': best_sellers,
            'new_arrivals': new_arrivals,
            'categories': categories,
            'faqs': faqs,
            'page_title': 'Sportig - Premium Sports & Lifestyle',
        })


class NewsletterSignupView(View):
    def post(self, request):
        email = request.POST.get('email', '').strip()
        if email:
            NewsletterSubscription.objects.get_or_create(email=email)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Thanks for subscribing!'
            })

        return redirect(request.META.get('HTTP_REFERER', '/'))


def error_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)


def robots_txt(request):
    content = """User-agent: *
Disallow: /admin/
Disallow: /users/
Disallow: /cart/
Disallow: /orders/
Disallow: /payments/
Sitemap: https://yourdomain.com/sitemap.xml"""
    return HttpResponse(content, content_type='text/plain')
