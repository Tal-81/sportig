# Sportig — Full-Stack Django Ecommerce

A production-ready ecommerce web application built with Django Template Architecture, PostgreSQL, Cloudinary, and Stripe.

---

## 🚀 Features

- **Custom User Model** with full address system
- **Product Management** with variants (size/color), gallery images, categories, brands
- **Advanced Search** using PostgreSQL full-text search
- **Cart System** — session-based (guests) + database (logged-in users)
- **Stripe Checkout** with webhook payment verification
- **PDF Invoice** generation with ReportLab
- **Wishlist**, **Reviews** (verified buyers only), **Coupons**, **Support Tickets**
- **Responsive Design** — Sportig -style UI with AOS + Swiper.js animations
- **Auto-logout** after 10 minutes of inactivity
- **Role-based permissions** — admin vs normal users
- **SEO** — sitemaps, robots.txt, meta tags, Open Graph
- **Heroku-ready** with Procfile, WhiteNoise, gunicorn

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 |
| Database | PostgreSQL |
| Storage | Cloudinary |
| Payments | Stripe |
| PDF | ReportLab |
| Static | WhiteNoise |
| Server | Gunicorn |
| Frontend | HTML + CSS + Vanilla JS + AOS + Swiper.js |

---

## ⚙️ Local Setup

### 1. Clone & create virtual environment
```bash
git clone https://github.com/tal-81/sportig.git
cd sportig
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and fill in your values
```

### 3. Create PostgreSQL database
```sql
CREATE DATABASE sportig_db;
```

### 4. Run migrations
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Collect static files
```bash
python manage.py collectstatic
```

### 6. Run development server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

---

## 💳 Stripe Setup (Test Mode)

1. Create a [Stripe account](https://stripe.com)
2. Copy your test keys to `.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```
3. Install Stripe CLI and forward webhooks locally:
   ```bash
   stripe listen --forward-to localhost:8000/payments/webhook/
   ```

---

## 📦 Cloudinary Setup

1. Create a [Cloudinary account](https://cloudinary.com)
2. Copy your credentials to `.env`:
   ```
   CLOUDINARY_CLOUD_NAME=your_name
   CLOUDINARY_API_KEY=your_key
   CLOUDINARY_API_SECRET=your_secret
   ```

---

## 🚢 Heroku Deployment

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:essential-0
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
heroku config:set CLOUDINARY_CLOUD_NAME=...
heroku config:set STRIPE_PUBLIC_KEY=...
heroku config:set STRIPE_SECRET_KEY=...
heroku config:set STRIPE_WEBHOOK_SECRET=...

git push heroku main
heroku run python manage.py createsuperuser
```

---

## 🧪 Running Tests

```bash
python manage.py test tests
```

---

## 📁 Project Structure

```
ecommerce/
├── users/          # Custom User model, auth views
├── products/       # Products, categories, brands, variants
├── cart/           # Session + DB cart system
├── orders/         # Order management, checkout
├── payments/       # Stripe integration + webhooks
├── reviews/        # Product reviews (verified buyers)
├── wishlist/       # User wishlist
├── coupons/        # Discount coupon system
├── support/        # Support ticket system
├── core/           # Homepage, sitemaps, context processors
├── services/       # PDF invoice generation
├── utils/          # Helper utilities
├── validators/     # Custom validators
├── templates/      # All HTML templates
├── static/         # CSS, JS, images
├── ecommerce/      # Django project config
├── requirements.txt
├── Procfile
├── .env.example
└── manage.py
```

---

## 🔑 Admin Panel

Access at `/admin/` with your superuser credentials.

**Admin Features:**
- Product management (add/edit/delete + variants + gallery)
- Order management + status updates
- Coupon management
- User management
- Support ticket management with replies
- Newsletter subscribers
- Hero banner management

---

## 💰 Currency

All prices are displayed in **Swedish Krona (kr / SEK)**.
Stripe payments are processed in `sek` Swedish Krona.
Fixed shipping: **100 kr**
Delivery: **3–5 business days**

---

## 🔒 Security Features

- CSRF protection on all forms
- HttpOnly session cookies
- Auto-logout after 10 minutes inactivity
- XSS protection headers
- Content Security Policy
- Secure Stripe webhook signature verification
- Database transactions to prevent overselling
- Admin accounts cannot be self-deleted
- Only verified buyers can leave reviews
