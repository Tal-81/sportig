from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from products.models import Product, Category, Brand, ProductVariant
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from reviews.models import Review
from wishlist.models import WishlistItem
from coupons.models import Coupon
from support.models import SupportTicket
from django.utils import timezone

User = get_user_model()


# ====================
# User Model Tests
# ====================
class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            first_name='Test',
            last_name='User',
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('TestPass123!'))

    def test_user_can_delete_account(self):
        self.assertTrue(self.user.can_delete_account())

    def test_admin_cannot_delete_account(self):
        admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='Admin123!'
        )
        self.assertFalse(admin.can_delete_account())

    def test_has_complete_address_false(self):
        self.assertFalse(self.user.has_complete_address())

    def test_has_complete_address_true(self):
        self.user.street_name = 'Main St'
        self.user.postal_code = '12345'
        self.user.city = 'Stockholm'
        self.user.country = 'Sweden'
        self.assertTrue(self.user.has_complete_address())

    def test_get_full_address(self):
        self.user.street_name = 'Main St'
        self.user.building_number = '10A'
        self.user.postal_code = '12345'
        self.user.city = 'Stockholm'
        self.user.country = 'Sweden'
        address = self.user.get_full_address()
        self.assertIn('Stockholm', address)
        self.assertIn('Sweden', address)


# ====================
# Product Model Tests
# ====================
class ProductModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Sneakers', slug='sneakers')
        self.brand = Brand.objects.create(name='Nike', slug='nike')
        self.product = Product.objects.create(
            name='Air Max 90',
            slug='air-max-90',
            description='Classic sneaker',
            price=Decimal('1299.00'),
            category=self.category,
            brand=self.brand,
            stock_quantity=10,
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Air Max 90')
        self.assertEqual(self.product.price, Decimal('1299.00'))
        self.assertTrue(self.product.is_in_stock)

    def test_current_price_no_discount(self):
        self.assertEqual(self.product.current_price, Decimal('1299.00'))

    def test_current_price_with_discount(self):
        self.product.discount_price = Decimal('999.00')
        self.assertEqual(self.product.current_price, Decimal('999.00'))

    def test_discount_percentage(self):
        self.product.discount_price = Decimal('999.00')
        expected = int(((1299 - 999) / 1299) * 100)
        self.assertEqual(self.product.discount_percentage, expected)

    def test_slug_auto_generated(self):
        product = Product.objects.create(
            name='Test Product',
            description='Test',
            price=Decimal('99.00'),
            category=self.category,
            stock_quantity=5,
        )
        self.assertEqual(product.slug, 'test-product')

    def test_get_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertIn('air-max-90', url)


# ====================
# Category Model Tests
# ====================
class CategoryModelTest(TestCase):

    def test_category_creation(self):
        cat = Category.objects.create(name='Running', slug='running')
        self.assertEqual(str(cat), 'Running')

    def test_category_slug_auto(self):
        cat = Category.objects.create(name='Gym Equipment')
        self.assertEqual(cat.slug, 'gym-equipment')


# ====================
# Cart Service Tests
# ====================
class CartServiceTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='cartuser', email='cart@test.com', password='Test1234!'
        )
        self.category = Category.objects.create(name='Test', slug='test')
        self.product = Product.objects.create(
            name='Test Shoe', slug='test-shoe', description='Test',
            price=Decimal('500.00'), category=self.category, stock_quantity=20
        )
        self.client = Client()

    def test_add_to_db_cart(self):
        from cart.services import CartService
        self.client.login(email='cart@test.com', password='Test1234!')
        request = self.client.get('/').wsgi_request
        request.user = self.user
        request.session = self.client.session

        success, msg = CartService.add_item(request, self.product.id, quantity=2)
        self.assertTrue(success)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_cart_total_calculation(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        self.assertEqual(cart.subtotal, Decimal('1500.00'))


# ====================
# View Tests
# ====================
class HomeViewTest(TestCase):

    def test_home_page_loads(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/home.html')

# =======================
# Product List View Tests
# =======================
class ProductListViewTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Sneakers', slug='sneakers')
        for i in range(5):
            Product.objects.create(
                name=f'Product {i}', slug=f'product-{i}',
                description='Test', price=Decimal('299.00'),
                category=self.category, stock_quantity=10
            )

    def test_product_list_loads(self):
        response = self.client.get(reverse('products:list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_search(self):
        response = self.client.get(reverse('products:list') + '?q=Product')
        self.assertEqual(response.status_code, 200)

    def test_product_category_filter(self):
        response = self.client.get(reverse('products:category', kwargs={'slug': 'sneakers'}))
        self.assertEqual(response.status_code, 200)

# =========================
# Product Detail View Tests
# =========================
class ProductDetailViewTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Test', slug='test-cat')
        self.product = Product.objects.create(
            name='Detail Product', slug='detail-product',
            description='A test product', price=Decimal('799.00'),
            category=self.category, stock_quantity=5
        )

    def test_product_detail_loads(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detail Product')

    def test_product_detail_404(self):
        response = self.client.get('/products/non-existent-slug/')
        self.assertEqual(response.status_code, 404)

# ====================
# User Auth Tests
# ====================
class UserAuthTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='authuser', email='auth@test.com', password='Auth1234!'
        )

    def test_register_view_get(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)

    def test_login_view_get(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'auth@test.com',
            'password': 'Auth1234!',
        })
        self.assertRedirects(response, reverse('core:home'))

    def test_profile_requires_login(self):
        response = self.client.get(reverse('users:profile'))
        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('users:profile')}")

    def test_profile_authenticated(self):
        self.client.login(email='auth@test.com', password='Auth1234!')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)

# ====================
# Cart View Tests
# ====================
class CartViewTest(TestCase):

    def test_cart_view_loads(self):
        response = self.client.get(reverse('cart:cart'))
        self.assertEqual(response.status_code, 200)

# ====================
# Wish List Tests
# ====================
class WishlistTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='wishuser', email='wish@test.com', password='Wish1234!'
        )
        self.category = Category.objects.create(name='Test', slug='test-wish')
        self.product = Product.objects.create(
            name='Wish Product', slug='wish-product',
            description='Test', price=Decimal('299.00'),
            category=self.category, stock_quantity=5
        )

    def test_toggle_wishlist_add(self):
        self.client.login(email='wish@test.com', password='Wish1234!')
        response = self.client.post(
            reverse('wishlist:toggle', kwargs={'product_id': self.product.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

    def test_toggle_wishlist_remove(self):
        WishlistItem.objects.create(user=self.user, product=self.product)
        self.client.login(email='wish@test.com', password='Wish1234!')
        self.client.post(
            reverse('wishlist:toggle', kwargs={'product_id': self.product.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

# ====================
# Coupon Tests
# ====================
class CouponTest(TestCase):

    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='TEST20',
            discount_percent=20,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timezone.timedelta(days=30),
            is_active=True,
            max_uses=100,
        )

    def test_valid_coupon(self):
        from coupons.services import CouponService
        discount, msg = CouponService.apply_coupon('TEST20', Decimal('1000.00'))
        self.assertEqual(discount, Decimal('200.00'))

    def test_invalid_coupon_code(self):
        from coupons.services import CouponService
        discount, msg = CouponService.apply_coupon('INVALID', Decimal('1000.00'))
        self.assertEqual(discount, 0)
        self.assertIn('Invalid', msg)

    def test_expired_coupon(self):
        from coupons.services import CouponService
        self.coupon.valid_to = timezone.now() - timezone.timedelta(days=1)
        self.coupon.save()
        discount, msg = CouponService.apply_coupon('TEST20', Decimal('1000.00'))
        self.assertEqual(discount, 0)

# ====================
# Support Ticket Tests
# ====================
class SupportTicketTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='supportuser', email='support@test.com', password='Sup1234!'
        )
        self.client.login(email='support@test.com', password='Sup1234!')

    def test_create_ticket(self):
        response = self.client.post(reverse('support:create'), {
            'subject': 'Test Issue',
            'message': 'This is a test support message.',
        })
        self.assertEqual(SupportTicket.objects.count(), 1)
        self.assertEqual(SupportTicket.objects.first().subject, 'Test Issue')

    def test_ticket_list_view(self):
        response = self.client.get(reverse('support:list'))
        self.assertEqual(response.status_code, 200)
