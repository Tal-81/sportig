# Sportig — Full-Stack Django Ecommerce

A production-ready ecommerce web application built with Django Template Architecture, PostgreSQL, Cloudinary, and Stripe.

---

- ![am i responsive](/photos_rm/AmIResponsive.png)
- live link - [Sportig](https://sportig-c80cb1dc5660.herokuapp.com)

## Introduction
   - Sportig is a full-stack e-commerce web application inspired by JD Sports, built with Django. The platform enables users to browse and purchase sportswear and athletic products from top brands, with a seamless shopping experience from discovery to checkout.
   Through the application, users can explore a wide range of products filtered by category, brand, gender, and price. Each product supports color and size variants, allowing customers to select exactly what they need before adding to cart. To complete a purchase, users pay securely via Stripe using a bank card.

---

## User Profiles

User Experience on Our Sports E-Commerce Platform (Sportig)

-  Browsing & Discovery:
Users find excitement and motivation in browsing our diverse array of premium athletic wear, sportswear, sportswear for kids, and high-performance sports equipment. They appreciate discovering new seasonal gear, checking size guides, and occasionally saving products to their wishlists or uploading size preferences for personalized fit recommendations.

-  Community & Engagement:
They take satisfaction in seeing community reviews and expert rating updates on gear and footwear. They value contributing to our active community by leaving feedback on product durability, fabric comfort, and sharing their fitness journeys.

-  Seamless Shopping & Management (Django Core):
Our Django-powered platform simplifies the checkout and ordering process, allowing users to secure the exact gear they need swiftly. The robust account functionality allows them to organize their order history, manage shipping addresses, track active deliveries, and explore tailored recommendations for men, women, and kids.

-  Curation & Sharing:
Users love collecting and organizing their favorite sportswear outfits and workout gear into customized wishlists. They enjoy curating their gym or outdoor equipment lists and sharing their favorite product finds with family and friends via social links.

-  Retention & Loyalty:
The seamless, responsive process of filtering products by category (Adults/Kids) and managing shopping carts is crucial. Users frequently log in to explore new arrivals, track their fitness gear upgrades, and enhance their overall active lifestyle experience.

---

## Design

### Wireframes section

- Mobile and iPad versions will share the same structure.
- Mobile - Home page wireframe.
- ![Mobile - Home page](/photos_rm/sportig_home_mobile_wireframe.png) 

- On mobile and iPad devices, clicking the hamburger icon opens the navigation menu, allowing users to access options such as services, contact, (log in, and register / cart, profile and logout). The menu remains open for easy navigation, and users should click the hamburger icon again to close it if user want it or click on anywhere except this menu.
---

- Mobile - All Products page wireframe
- ![Mobile - All Products page](/photos_rm/sportig_allproducts_mobile_wireframe.png)

---

- Mobile - Sign Up page wireframe.
- ![Mobile - sign up page](/photos_rm/sportig_signup_mobile_wireframe.png)

---

- Mobile - Product Details page wireframe.
- ![Mobile - Product Details page](/photos_rm/sportig_details_mobile_wireframe.png)

---

- Desktop and wide screen devices versions will share the same structure.
- Desktop - Home page wireframe
- ![Desktop - Home page](/photos_rm/wf-desktop-homepage.png)

---

- Desktop - All Products page wireframe
- ![Desktop - All Products page](/photos_rm/wf-desktop-allproducts.png)

---

- Desktop - Sign Up page wireframe
- ![Desktop - Sign Up page](/photos_rm/wf-desktop-signup.png)

---

- Desktop - Product Details page wireframe
- ![Desktop - Product Details page](/photos_rm/wf-desktop-details.png)

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
- **Toaster messages** are used to provide real-time feedback for user actions

---

###   User Goals
The Casual Browser:

-  These users seek to discover the latest trends in sportswear, activewear, and athletic gear. They enjoy browsing through new arrivals, seasonal collections (for men, women, and kids), and athletic styles as a relaxing way to get inspired for their fitness journey or casual everyday wear.

The Goal-Oriented Shopper:

-  This group uses the platform with a clear intent: to buy specific training clothes, sportswear, or sports equipment. They appreciate smart product filters (by size, gender, or sport type), detailed product descriptions, reliable size guides, customer reviews, and a seamless, secure checkout experience to get their gear quickly.

The Fitness Enthusiast:

-  Dedicated athletes and fitness lovers who enjoy finding and collecting premium high-performance gear. They take pride in building customized wishlists, tracking their workout equipment upgrades, organizing their order history, and gathering knowledge on fabric technologies (like sweat-wicking or 100% cotton).

###   Website Owner Goals
Traffic & Conversion Growth:

-  The owner's primary goal is to increase website traffic and conversion rates. Attracting more fitness enthusiasts and families leads to higher sales volume and opportunities to scale the brand.

Revenue & Business Scalability:

-  This growth directly drives increased revenue from direct product sales, bundled equipment packages, and exclusive drops. The robust Django backend ensures the platform can easily scale to support higher transaction volumes and future loyalty programs.

Customer Retention & Satisfaction:

-  New features (like smart product recommendations or user reviews) must be carefully implemented to keep existing shoppers satisfied, loyal, and engaged without cluttering the shopping experience.

Cross-Platform Seamlesness (Responsive UI):

-  The storefront must function flawlessly and fast on both mobile devices and desktops. This ensures users can effortlessly browse, add items to their cart, and complete payments securely on any screen size.

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

## Deployment

- Deploy the project on __Github Pages__.
  - Enable GitHub Pages
    - Go to Your Repository on GitHub: Navigate to your repository in your web browser.

  - Access Repository Settings:
    - Click on the "Settings" tab.
    - Scroll to GitHub Pages:
    - Find the "Pages" section in the left sidebar.
    - Under the "Source" section, select the branch you want to use (usually main or master).
    - If needed, select the / (root) folder for your project.
    - Save Your Changes: Click "Save" if prompted.

  - Access Your Deployed Site View Your Site:
    - After enabling GitHub Pages, your site will be available at https://username.github.io/repository-name/ (or https://username.github.io/ for user sites).
    - It may take a few minutes for the site to be accessible.
    - Check for Issues: If the page doesn’t load, ensure your index.html file is in the root directory, as GitHub Pages defaults to looking for this file.

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

---

## DataBase Models

### Users

| Name       | KYE             | TYPE             | EXTRA                            |
| ---------- | --------------- | ---------------- | -------------------------------- |
| user       | OneToOneField   | User             | on_delete=models.CASCADE, related_name='profile'|
| email      | EmailField      | Email            | unique=True                      |
| phone      | CharField       | String(max=20)   | blank=True                       |
| avatar     | CloudinaryField | Image            | default=DEFAULT_AVATAR, blank=True, null=True |
| bio        | TextField       | Text             | blank=True                       |

### Category

| Name       | KYE           | TYPE                   | EXTRA                                |
| ---------- | ------------- | ---------------------- | ------------------------------------ |
| category   | CharField     | String (max=60)        | choices=CATEGORY_CHOICES, unique=True|
| price_per_15min| DecimalField| Decimal              | max_digits=10, decimal_places=2      |
| description| TextField     | Text                   | blank=True                           |

### Products

| Name       | KYE             | TYPE                   | EXTRA                                     |
| ---------- | --------------- | ---------------------- | ----------------------------------------- |
| user       |  ForeignKey     | User                   |on_delete=models.CASCADE, related_name='appointments'|
| category   | ForeignKey      | ConsultationCategory   | on_delete=models.CASCADE, related_name='appointments'|
| date       | DateField       | Date                   | CASCADE, related_name='comments'          |
| time       | TimeField       | Time                   | auto_now_add=True (Set once when created) |
| duration   | IntegerField    | Integer                | choices=DURATION_CHOICES                  |
| total_price| DecimalField    | Decimal                | max_digits=10, decimal_places=2, editable=False, default=0|
| is_paid    | BooleanField    | Boolean                | default=False                             |
| created_at | DateTimeField   | DateTime               | auto_now_add=True                         |

### Cart

| Name       | KYE           | TYPE                   | EXTRA                                     |
| ---------- | ------------- | ---------------------- | ----------------------------------------- |
| user       | OneToOneField | User                   | on_delete=models.CASCADE, related_name='cart'|
| post       | DateTimeField | DateTime               | auto_now_add=True                         |
| created_at | DateTimeField | DateTime               | auto_now=True                             |

### CartItem

| Name           | KYE                  | TYPE                   | EXTRA                                     |
| -------------- | -------------------- | ---------------------- | ----------------------------------------- |
| cart           | ForeignKey           | Cart                   | on_delete=models.CASCADE, related_name='items' |
| category       | ForeignKey           | ConsultationCategory   | on_delete=models.CASCADE |
| date           | DateField            | Date                   |                          |
| time           | TimeField            | Time                   |                          |
| created_at     | DateTimeField        | -                      |                          |
| duration       | IntegerField         | Integer                | choices=DURATION_CHOICES |
| added_at       | DateTimeField        | DateTime               | auto_now_add=True        |

### Order

| Name       | KYE           | TYPE   | EXTRA                                           |
| ---------- | ------------- | ------ | ----------------------------------------------- |
| user       | ForeignKey    | User   | on_delete=models.CASCADE, related_name='orders' |
| total_amount| DecimalField | Decimal| max_digits=10, decimal_places=2                 |
| status     | CharField     | String | choices=STATUS_CHOICES, default='pending'       |
| stripe_payment_intent_id | CharField | String | max_length=255, blank=True            |
| created_at  | DateTimeField| DateTime| auto_now_add=True                              |
| updated_at  | DateTimeField | DateTime | auto_now=True                                |

### OrderItem

| Name       | KYE           | TYPE | EXTRA                                |
| ---------- | ------------- | ---- | ------------------------------------ |
| order      | ForeignKey    | Order| on_delete=models.CASCADE, related_name='items'|
| category   | ForeignKey    | ConsultationCategory| on_delete=models.SET_NULL, null=True|
| category_name| CharField   | String (max=60)| Snapshot name |
| date       | DateField     | Date | on_delete=models.SET_NULL, null=True|
| time       | TimeField     | Time | on_delete=models.CASCADE, related_name='items'|
| duration   | IntegerField  | Integer| choices=DURATION_CHOICES |
| unit_price | DecimalField  | Decimal| max_digits=10, decimal_places=2 |
| total_price| DecimalField  | Decimal| max_digits=10, decimal_places=2 |
| appointment| OneToOneField | Appointment| on_delete=models.SET_NULL, null=True, blank=True|

### Support

Model inherits fields from AbstractUser
| Name | KYE | TYPE | EXTRA |
| ---------- | ------------- | ---- | -------------------- |
|user| ForeignKey| User | on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages'|
|name| CharField| String (max=100) |  |
|email| EmailField| Email |  |
|subject| CharField| String (max=30) |choices=SUBJECT_CHOICES, default='general'|
|message|TextField| Text | |
|created_at|DateTimeField| DateTime|auto_now_add=True|
|is_read|BooleanField| Boolean | default=False|

### Reviews

Model inherits fields from AbstractUser
| Name | KYE | TYPE | EXTRA |
| ---------- | ------------- | ---- | -------------------- |
|user| ForeignKey| User | on_delete=models.SET_NULL, null=True, blank=True, related_name='contact_messages'|
|name| CharField| String (max=100) |  |
|email| EmailField| Email |  |
|subject| CharField| String (max=30) |choices=SUBJECT_CHOICES, default='general'|
|message|TextField| Text | |
|created_at|DateTimeField| DateTime|auto_now_add=True|
|rate|IntegerField| Integer | default=0|
|is_read|BooleanField| Boolean | default=False|

---

## Manual test

### Nav-bar

| Tasks                                                                                                               | Yes | No  |
| ------------------------------------------------------------------------------------------------------------------- | --- | --- |
| Click on Sportig home page load.                                                                                     | x   |     |
| Click on home icon, home page load.                                                                                 | x   |     |
| Click on login, form login page load.                                                                              | x   |     |
| Click on register, form register page load.                                                                         | x   |     |
| On smaller screen navbar turn to hamburger icon.                                                                    | x   |     |
| click on hamburger icon it will expand.                                                                             | x   |     |
| Hamburger icon expands shows(Shop By, Category, Gender) before login.                                                    | x   |     |


---

### Home page.

| Tasks                                                                        | Yes | No  |
| ---------------------------------------------------------------------------- | --- | --- |
| Page loads.                                                                  | x   |     |
| If you are not logged in, you will not be able to complete shopping.                | x   |     |
| If you are logged in, you will be able to payment.                 | x   |     |
| Click on heart icon, the product will add to your wishlist.                   | x   |     |
| Click on heart icon when you are logged out, redirect you to login page .          | x   |     |
| Click on payment in stripe form, it will show you a success message.             | x   |     |
| All home page sections works. | x   |     |
| Click on next/prev button in the slider will show other image.       | x   |     |

---

### Register page

| Tasks                                                                     | Yes | No  |
| ------------------------------------------------------------------------- | --- | --- |
| Page load.                                                                | x   |     |
| Click on register, form load to create new user.                          | x   |     |
| The form should not be any blank fields.                                  | x   |     |
| Both passwords must match.                                                | x   |     |
| click on Register, successful register you are taken to the sign in page. | x   |     |

---

### Login

| Tasks                                              | Yes | No  |
| -------------------------------------------------- | --- | --- |
| Click on Login, dispaly form for login page.       | x   |     |
| Form shouldn't be blank.                            | x   |     |
| Just you can sign by email, not user name.       | x   |     |
| After login, logout, cart and profile display in the navbar. | x   |     |

---

### buy a new product.

| Tasks                                                            | Yes | No  |
| ---------------------------------------------------------------- | --- | --- |
| You should be logged in to have ability to paying.                    | x   |     |
| Click on buy button, you will move to product page.                     | x   |     |
| Error Message will displays if user do a mistake         | x   |     |
| Check product availability when increase product count .                         | x   |     |
| Choose colour, size and count for product before purchase.                      | x   |     |
| When the payment is done there is a success toast notification | x   |     |

---

### Profile

| Tasks                                                                                             | Yes | No  |
| ------------------------------------------------------------------------------------------------- | --- | --- |
| You must be logged in to access Profile. page.                                                  | x   |     |
| Payment History table shows all orders.          | x   |     |
| Profile form fields will display all user information.              | x   |     |
| Upload avatar is working.                                     | x   |     |
| For every action performed, the appropriate message will be displayed in the top-right corner. | x   |     |
| Change password form works.                                     | x   |     |


---

## Validation

  **Document checking completed. No errors or warnings to show.**
- I tested all my pages and result was no error in html, css and javascript code.
- I have validated all my __html__ files using the W3C Validator, and no errors were found.
### index.html
- ![index html test](/photos_rm/validator/html_validator.png)

---
- I have validated all my __JavaScript__ and JSX files using ESLint, and no errors were found.
### main.js
- ![main js test](/photos_rm/validator/js_validator.png)

---
### main.css
- I have validated all my __CSS__ files using the W3C Jigsaw Validator, and no errors were found.
- ![css test](/photos_rm/validator/css_validator.png)

---
### python files
- I have validated all my __PYTHON__ files using P8P linter, and no errors were found.
- I used [PEP8 CI Python linter](https://pep8ci.herokuapp.com/) validation to all my files, and Results:
  All clear, no errors found.
- ![css test](/photos_rm/validator/py_cart_views.png)
- ![css test](/photos_rm/validator/py_core_views.png)
- ![css test](/photos_rm/validator/py_coupon_views.png)
- ![css test](/photos_rm/validator/py_orders_views.png)
- ![css test](/photos_rm/validator/py_payments_views.png)
- ![css test](/photos_rm/validator/py_products_views.png)
- ![css test](/photos_rm/validator/py_reviews_views.png)
- ![css test](/photos_rm/validator/py_support_views.png)
- ![css test](/photos_rm/validator/py_users_views.png)

---

### manual test for python files
- I used an integrated middleware in django for testing units (functions) in python files.
  All clear, no errors found.
- service service:
- ![service service test](/photos_rm/manual-test/cart_service.png)
- ![service service test result](/photos_rm/manual-test/cart_service_result.png)
---
- service view:
- ![service view test](/photos_rm/manual-test/cart_view.png)
- ![service view test result](/photos_rm/manual-test/cart_view_result.png)
---
- category model:
- ![category model test](/photos_rm/manual-test/category_model.png)
- ![category model test result](/photos_rm/manual-test/category_model_result.png)
---
- coupon:
- ![coupon test](/photos_rm/manual-test/coupon.png)
- ![coupon test result](/photos_rm/manual-test/coupon_result.png)
---
- homepage view:
- ![home page view test](/photos_rm/manual-test/home_page_view.png)
- ![home page view test result](/photos_rm/manual-test/home_page_view_result.png)
---
- product detail view :
- ![product detail view test](/photos_rm/manual-test/product_detail_view.png)
- ![product detail view test result](/photos_rm/manual-test/product_detail_view_result.png)
---
- product list view:
- ![product list view test](/photos_rm/manual-test/product_list_view.png)
- ![product list view test result](/photos_rm/manual-test/product_list_view_result.png)
---
- product model:
- ![product model test](/photos_rm/manual-test/product_model.png)
- ![product model test result](/photos_rm/manual-test/product_model_result.png)
---
- support ticket:
- ![support ticket test](/photos_rm/manual-test/support_ticket.png)
- ![support ticket test result](/photos_rm/manual-test/support_ticket_result.png)
---
- user auth:
- ![user auth test](/photos_rm/manual-test/user_auth.png)
- ![user auth test result](/photos_rm/manual-test/user_auth_result.png)
---
- user model:
- ![user model test](/photos_rm/manual-test/user_model.png)
- ![user model test result](/photos_rm/manual-test/user_model_result.png)
---
- wish list:
- ![wish list test](/photos_rm/manual-test/wish_list.png)
- ![wish list test result](/photos_rm/manual-test/wish_list_result.png)
---

### Lighthouse test
- ![lighthouse test](/photos_rm/lighthouse_test.png)

### Stripe payment test
- ![Stripe test](/photos_rm/stripe.png)

---

## Postman

- Tool Used: Postman        
- Base URL: https://sportig-c80cb1dc5660.herokuapp.com/
- Authentication: Token-based authentication used for secured endpoints.

- The Postman collection file for this project is located at [postman](https://github.com/Tal-81/sportig/blob/main/Sportig_API_Tests.postman_collection.json) .
- You can import this file into Postman to access the collection of API endpoints and test them.
- Import from postman
- Open Postman.
- Dropdown three dots next to you app name.
- Click on export.
- This will direct you to your computer files where you can choose to locate your postman file.
- By importing the Postman collection, you can seamlessly access and test the API endpoints of the Task Management System for functionality.
- I have thoroughly tested all my apps using Postman to ensure that the CRUD operations function correctly.
- You can import this file into Postman to access the collection of API endpoints and test them.
- First you need to setup the environment by get on CSRF token:
[CSRF](/photos_rm/postman/Get_CSRF_Token_First_Step.png) .
- Test parts by postman for this project:
[test sections](/photos_rm/postman/test-parts.png) .
- The Result of Testing by Postman collection file for this project is located at [postman](https://github.com/Tal-81/sportig/blob/main/Sportig_Result_Full%20Test.Postman_test_run.json) .

---
## Bugs
- CSS Validator asks me to add header html element h1 or h2 inside section element or add div instead of section tag if I do not need to add header tag inside this section.
  - I changed section element to div element:
  - ![error message](/photos_rm/error/change_section_to_div_1.png)
---
- Web browser cannot recongnize the property line-clamp in css because it is modern property and warn me.
  - Line-clamp css property is a new property:
  - ![line-clamp property undefined](/photos_rm/error/css_validator_line_clamp.png)
  - Added text-overflow instead of line-clamp:
  - ![remove line-clamp property](/photos_rm/error/css_validator_line_clamp_resolve.png)
---
- Some meta and link html tags exist inside body tag when the project runs on web browser:
  - The reason was {%csrf_token%} percent sign made broken to my code in the web browser for that I remove it {%CSRF_token%} from head html tag and so I fix the error.
  - Lighthouse warning message:
  - ![form element with no label](/photos_rm/error/meta_link_tag_inside_body_2.png)
  - Lighthouse warning message:
  - ![form element with no label](/photos_rm/error/meta_link_tag_inside_body.png)
  - Lighthouse warning message:
  - ![form element with no label](/photos_rm/error/meta_link_tag_inside_body_3.png)
---
- Refactored from a ternary operator to a standard 'if' statement since an 'else' block wasn't required:
  - Replaced a ternary operator with a traditional if statement. Because ternary operators strictly require both truthy and falsy (else) expressions, and our logic only needed a single unconditional if execution, a standard if block was the most syntactically appropriate and readable choice.
---

## Credits
- I would like to extend my sincere appreciation to Code Institute for granting me extra time to complete this project. Their support and flexibility allowed me to refine my work and ensure I met all the necessary requirements. I am grateful for the opportunity to improve and successfully complete this milestone.
- Inspiration_
  - The design and layout of the front-end were inspired by a similar website I came across  [- ( Snaps ) -](https://snaps-frontend-871b3764ee9c.herokuapp.com/). No code was copied; I only used it as a reference for the visual structure and user experience.
- AI model that Open AI Chatgpt was used to solve some buges.

---