"""
Product views: listing, detail, search, filtering.
Uses effective_price annotation to filter by discount_price when set,
otherwise falls back to regular price.
"""

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.postgres.search import (
    SearchVector, SearchQuery, SearchRank)
from django.db.models import Min, Max, Case, When, F, DecimalField, Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import Product, Category, Brand, ProductVariant

GENDER_CHOICES = [
    ('', 'All'),
    ('men', 'Men'),
    ('women', 'Women'),
    ('kids', 'Kids'),
    ('unisex', 'Unisex'),
]

# Annotation that resolves to the real selling price:
# discount_price if it exists, otherwise regular price
EFFECTIVE_PRICE_ANNOTATION = Case(
    When(
        discount_price__isnull=False,
        then=F('discount_price'),
    ),
    default=F('price'),
    output_field=DecimalField(max_digits=10, decimal_places=2),
)


def _annotate_effective_price(qs):
    'Annotate a queryset with 'effective_price' (discount or regular price).'
    return qs.annotate(effective_price=EFFECTIVE_PRICE_ANNOTATION)


class ProductListView(View):
    template_name = 'products/list.html'
    paginate_by = 12

    def get(self, request):
        products = Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        ).prefetch_related('reviews', 'variants')

        # Full-text search
        query = request.GET.get('q', '').strip()
        if query:
            search_vector = (
                SearchVector('name', weight='A') +
                SearchVector('description', weight='B')
            )
            search_query = SearchQuery(query)
            products = products.annotate(
                rank=SearchRank(search_vector, search_query)
            ).filter(rank__gte=0.01).order_by('-rank')

        # Filters
        category_slug = request.GET.get('category', '')
        gender = request.GET.get('gender', '')
        brand_id = request.GET.get('brand', '')
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()
        sort_by = request.GET.get('sort', 'newest')

        if category_slug:
            products = products.filter(category__slug=category_slug)
        if gender:
            products = products.filter(gender=gender)
        if brand_id:
            products = products.filter(brand_id=brand_id)

        # Price range filter using effective_price
        # (discount_price if set, otherwise regular price)
        if min_price or max_price:
            products = _annotate_effective_price(products)
            if min_price:
                try:
                    products = products.filter(
                        effective_price__gte=float(min_price)
                    )
                except ValueError:
                    pass
            if max_price:
                try:
                    products = products.filter(
                        effective_price__lte=float(max_price)
                    )
                except ValueError:
                    pass

        # Sorting
        if not query:
            sort_map = {
                'price_asc': 'price',
                'price_desc': '-price',
                'newest': '-created_at',
                'popular': '-sales_count',
            }
            products = products.order_by(sort_map.get(sort_by, '-created_at'))

        # Pagination
        paginator = Paginator(products, self.paginate_by)
        page_obj = paginator.get_page(request.GET.get('page', 1))

        # Price range for slider/inputs — use real effective minimum/maximum
        price_range = Product.objects.filter(is_active=True).annotate(
            effective_price=EFFECTIVE_PRICE_ANNOTATION
        ).aggregate(
            min_price=Min('effective_price'),
            max_price=Max('effective_price'),
        )

        return render(request, self.template_name, {
            'products': page_obj,
            'categories': Category.objects.filter(is_active=True),
            'brands': Brand.objects.filter(is_active=True),
            'genders': GENDER_CHOICES,
            'query': query,
            'selected_category': category_slug,
            'selected_gender': gender,
            'selected_brand': brand_id,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': sort_by,
            'price_range': price_range,
            'total_count': paginator.count,
            'page_title': f'Search: {query}' if query else 'All Products',
        })


class ProductDetailView(View):
    template_name = 'products/detail.html'

    def get(self, request, slug):
        product = get_object_or_404(
            Product.objects.select_related(
                'category', 'brand'
                ).prefetch_related(
                'gallery_images', 'variants', 'reviews__user'
            ),
            slug=slug, is_active=True
        )

        # Increment view count atomically
        Product.objects.filter(pk=product.pk).update(
            views_count=product.views_count + 1
        )

        # Track recently viewed in session
        recently_viewed = request.session.get('recently_viewed', [])
        if product.id not in recently_viewed:
            recently_viewed.insert(0, product.id)
            recently_viewed = recently_viewed[:10]
            request.session['recently_viewed'] = recently_viewed

        # Related products in same category
        related_products = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(pk=product.pk).select_related('category')[:8]

        # Unique colors from variants
        colors_seen = set()
        colors = []
        for v in product.variants.all():
            if v.color not in colors_seen:
                colors.append({'color': v.color, 'hex': v.color_hex})
                colors_seen.add(v.color)

        # Review eligibility (verified buyers only)
        can_review = False
        user_review = None
        if request.user.is_authenticated:
            from orders.models import OrderItem
            can_review = OrderItem.objects.filter(
                order__user=request.user,
                product=product,
                order__status='delivered'
            ).exists()
            user_review = product.reviews.filter(user=request.user).first()

        return render(request, self.template_name, {
            'product': product,
            'related_products': related_products,
            'colors': colors,
            'can_review': can_review,
            'user_review': user_review,
            'page_title': product.name,
        })


class CategoryView(View):
    template_name = 'products/list.html'

    def get(self, request, slug):
        category = get_object_or_404(Category, slug=slug, is_active=True)
        products = Product.objects.filter(
            category=category, is_active=True
        ).select_related('brand').prefetch_related('reviews', 'variants')

        gender = request.GET.get('gender', '')
        sort_by = request.GET.get('sort', 'newest')
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()

        if gender:
            products = products.filter(gender=gender)

        # Price filter using effective_price
        if min_price or max_price:
            products = _annotate_effective_price(products)
            if min_price:
                try:
                    products = products.filter(
                        effective_price__gte=float(min_price)
                    )
                except ValueError:
                    pass
            if max_price:
                try:
                    products = products.filter(
                        effective_price__lte=float(max_price)
                    )
                except ValueError:
                    pass

        sort_map = {
            'price_asc': 'price',
            'price_desc': '-price',
            'newest': '-created_at',
            'popular': '-sales_count',
        }
        products = products.order_by(sort_map.get(sort_by, '-created_at'))

        paginator = Paginator(products, 12)
        page_obj = paginator.get_page(request.GET.get('page', 1))

        price_range = Product.objects.filter(
            category=category, is_active=True
        ).annotate(
            effective_price=EFFECTIVE_PRICE_ANNOTATION
        ).aggregate(
            min_price=Min('effective_price'),
            max_price=Max('effective_price'),
        )

        return render(request, self.template_name, {
            'products': page_obj,
            'category': category,
            'categories': Category.objects.filter(is_active=True),
            'brands': Brand.objects.filter(is_active=True),
            'genders': GENDER_CHOICES,
            'selected_category': slug,
            'selected_gender': gender,
            'sort_by': sort_by,
            'min_price': min_price,
            'max_price': max_price,
            'total_count': paginator.count,
            'price_range': price_range,
            'page_title': category.name,
        })


class GetVariantSizesView(View):
    """AJAX: return available sizes for a product + color combination."""

    def get(self, request, product_id):
        color = request.GET.get('color', '')
        variants = ProductVariant.objects.filter(
            product_id=product_id,
            color=color,
            stock_quantity__gt=0,
        ).values('id', 'size', 'stock_quantity')
        return JsonResponse({'variants': list(variants)})


class RecentlyViewedView(View):
    template_name = 'products/recently_viewed.html'

    def get(self, request):
        recently_viewed_ids = request.session.get('recently_viewed', [])
        products = list(
            Product.objects.filter(
                id__in=recently_viewed_ids, is_active=True
            ).select_related('category')
        )
        # Preserve the session order
        products.sort(
            key=lambda p: recently_viewed_ids.index(p.id)
            if p.id in recently_viewed_ids else 99
        )
        return render(request, self.template_name, {
            'products': products,
            'page_title': 'Recently Viewed',
        })
