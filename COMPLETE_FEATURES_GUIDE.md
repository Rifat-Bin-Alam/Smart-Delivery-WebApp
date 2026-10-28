# SwiftDrop — Complete Technical & Functional Architecture Guide

> **Tagline:** Your Essentials. Delivered Smarter.  
> **Repository:** [https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp](https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp)  
> **Author & Lead Developer:** [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/)  
> **Contact Email:** [rifat5566123@gmail.com](mailto:rifat5566123@gmail.com)  
> **Version:** 2.0 (Production-Ready Architecture)  
> **Platform Language:** English Only

---

## Table of Contents
1. [Executive Summary & Project Scope](#1-executive-summary--project-scope)
2. [Architectural Pattern & Directory Structure](#2-architectural-pattern--directory-structure)
3. [Core Django Applications & Modular Responsibilities](#3-core-django-applications--modular-responsibilities)
4. [Data Layer & Entity Relationship Architecture](#4-data-layer--entity-relationship-architecture)
5. [Complete End-to-End Business Workflows](#5-complete-end-to-end-business-workflows)
6. [Feature Implementation Matrix: Production vs. Simulated Sandbox](#6-feature-implementation-matrix-production-vs-simulated-sandbox)
7. [Frontend Design System, Component Library & UX Patterns](#7-frontend-design-system-component-library--ux-patterns)
8. [Static Assets, Category Fallbacks & Media Pipeline](#8-static-assets-category-fallbacks--media-pipeline)
9. [Forms, Validation Rules & Server-Side Integrity](#9-forms-validation-rules--server-side-integrity)
10. [Security Engineering & Authentication Framework](#10-security-engineering--authentication-framework)
11. [Database Schema, Indexing & Migration History](#11-database-schema-indexing--migration-history)
12. [Automated Testing Suite & Verification Protocol](#12-automated-testing-suite--verification-protocol)
13. [Deployment Readiness & Production Configuration](#13-deployment-readiness--production-configuration)
14. [Local Development & Demo Credentials](#14-local-development--demo-credentials)
15. [Future Roadmap & Enterprise Hardening Recommendations](#15-future-roadmap--enterprise-hardening-recommendations)

---

## 1. Executive Summary & Project Scope

**SwiftDrop** is a robust, full-stack on-demand delivery platform engineered to facilitate rapid hyperlocal dispatch of daily essentials—including fresh food, prescription pharmaceuticals, domestic LPG cooking gas cylinders, and packaged groceries. 

Built with **Python 3.13**, **Django 5.2**, and an optimized relational schema, SwiftDrop addresses the entire lifecycle of an order:
* **Customer Facing Portal:** Frictionless authentication, dynamic catalog exploration, client-side cached shopping cart with server-side validation, checkout with area-based fee calculation, real-time status tracker, and verified feedback loop.
* **Delivery Agent Hub:** Dedicated portal for order acceptance, location ping updates, dispatch verification, and fulfillment logs.
* **Administrative Operations:** Centralized control deck for inventory stock control, status transition overrides, financial auditing, and user moderation.

---

## 2. Architectural Pattern & Directory Structure

SwiftDrop follows the classic **Django Model-Template-View (MTV)** pattern, augmented with a modern decoupled frontend design system powered by Bootstrap 5, Vanilla JavaScript ES6 modules, and FontAwesome 6 icons.

```
Smart-Delivery-WebApp/
├── Nagaribashi_express/            # Django Project Root & Orchestration
│   ├── __init__.py
│   ├── asgi.py                     # ASGI asynchronous server hook
│   ├── settings.py                 # Core unified application settings
│   ├── settings_production.py      # Production hardening overrides
│   ├── urls.py                     # Root URL routing table
│   └── wsgi.py                     # WSGI production application hook
├── users/                          # User accounts, RBAC & profile management
├── orders/                         # Product catalog, cart, checkout & fulfillment
├── delivery/                       # Driver assignments, zone dispatch & tracking
├── payments/                       # Billing, transaction ledger & refund engine
├── reviews/                        # Verified customer ratings & feedback loop
├── dashboard/                      # Analytics, home portal, administrative metrics
├── templates/                      # Modular Django HTML5 templates
│   ├── base.html                   # Global layout skeleton, navbar & footer
│   ├── dashboard/                  # Home, contact, admin & stats views
│   ├── delivery/                   # Driver assignment & delivery area views
│   ├── orders/                     # Catalog, cart, checkout, tracking & detail
│   ├── payments/                   # Invoice, receipt & transaction logs
│   ├── reviews/                    # Rating submissions & review lists
│   └── users/                      # Authentication, profile & dashboard views
├── static/                         # Static CSS, JavaScript, illustrations & fonts
│   ├── css/                        # Custom stylesheet & design system
│   ├── js/                         # main.js, cart engine & dynamic UI scripts
│   └── images/
│       ├── logo.svg                # Brand vector identity
│       └── fallbacks/              # 9 Category vector SVG illustrations
├── media/                          # Uploaded product imagery and avatars
├── manage.py                       # Django CLI management executable
├── requirements.txt                # Python environment dependencies
└── .env.example                    # Environment configuration template
```

---

## 3. Core Django Applications & Modular Responsibilities

| Application | Primary Role | Key Endpoints / Responsibilities |
|---|---|---|
| `users` | Identity & RBAC | Custom User model, session auth, CustomerProfile, DeliveryAgentProfile, email login. |
| `orders` | Commerce & Fulfillment | ProductService catalog, cart management, checkout engine, Order state machine, order cancellation. |
| `delivery` | Logistics & Dispatch | DeliveryAssignment, driver geolocations, DeliveryArea fee tables, live order status tracker. |
| `payments` | Transactions & Ledgers | Payment entity, PaymentMethod registry (COD, bKash, Nagad), simulated transaction logger, refund records. |
| `reviews` | Quality & Feedback | Verified purchase reviews, star ratings (1-5), helpful vote tallies, admin moderation, and seller responses. |
| `dashboard` | Operations & Metrics | Landing page, administrative control center, live KPI analytics, FAQs, and system audit logs. |

---

## 4. Data Layer & Entity Relationship Architecture

### 4.1. Entity Relationships Overview
```
           +-------------------+
           |    users.User     | (AbstractUser with email authentication)
           +---------+---------+
                     |
       +-------------+-------------+
       | 1:1                       | 1:1
+------+--------------+    +------+------------------+
| CustomerProfile     |    | DeliveryAgentProfile    |
+---------------------+    +-------------------------+
       | 1:N                       | 1:N
       v                           v
+---------------------+    +-------------------------+
|    orders.Order     |<---| delivery.Assignment     |
+----------+----------+    +-------------------------+
           | 1:N                           | 1:N
           v                               v
+---------------------+    +-------------------------+
|  orders.OrderItem   |    | delivery.DeliveryStatus |
+----------+----------+    +-------------------------+
           | N:1
           v
+---------------------+
| orders.ProductService|
+---------------------+
```

### 4.2. Database Model Schema Highlights
* **`User`**: Extends `AbstractUser`. Uses `email` as the primary authentication identifier with `username` as a required secondary attribute. Fields include `phone_number` (unique), `user_type` (`customer`, `admin`, `delivery_agent`), `address`, `city`, `postal_code`, and `is_verified`.
* **`ProductService`**: Contains `name`, `category` (choice field), `price` (DecimalField in BDT), `stock_quantity` (PositiveIntegerField), `image` (ImageField), and `is_available` (BooleanField). Features an intelligent dynamic property `image_url` that serves the uploaded asset or seamlessly falls back to a category-specific SVG.
* **`Order`**: Houses `order_number` (unique generated string), `customer` (FK), `delivery_address`, `delivery_city`, `status` (`pending`, `confirmed`, `processing`, `delivered`, `cancelled`, `refunded`), `delivery_fee`, and calculated `total_amount`.
* **`OrderItem`**: Line-item tracking linking an `Order` with a `ProductService`, capturing captured `unit_price`, `quantity`, and calculated `total_price`.
* **`Payment`**: Captures financial transaction attempts, linking to `Order` and `PaymentMethod`, storing unique `transaction_id`, `amount`, and `status`.

---

## 5. Complete End-to-End Business Workflows

### 5.1. Customer Registration & Authentication
1. Prospective user accesses `/users/signup/` and submits email, username, phone number, and password.
2. Form validates phone formatting and ensures unique email. A `CustomerProfile` is created via Django signals upon user persistence.
3. User signs in via `/users/login/` utilizing the email-based backend.

### 5.2. Product Browsing, Filtering & Search
1. Customers navigate to `/orders/products/`.
2. Interactive category pills filter the DOM dynamically without page reloads, while the server-side view handles category slugs via `/orders/category/<slug>/`.
3. Client-side search filters the product grid in real time with responsive fallback cards when no matches are found.

### 5.3. Shopping Cart & Live Server-Side Pricing
1. Customers add items to their cart. The client stores items in `localStorage` through `static/js/main.js` (`SwiftDropCart`).
2. Badge count and subtotal recalculate instantly across tabs through custom DOM events (`swiftdrop:cart-updated`).
3. When the user proceeds to checkout, the raw cart payload is sent to `/orders/checkout/` where Django queries the database to retrieve true, tamper-proof current prices and stock availability.

### 5.4. Checkout & Order Placement
1. The user inputs their delivery address, recipient contact, delivery area zone, and preferred payment option (COD, bKash, Nagad, Card).
2. Django wraps order creation in an `atomic` database transaction:
   - Verifies item stock quantities.
   - Calculates delivery fee from the selected `DeliveryArea`.
   - Generates an immutable `Order` record and associated `OrderItem` entries.
   - Decrements product inventory stock.
   - Creates an initial `OrderStatusHistory` entry.
3. The cart is cleared upon redirect to `/orders/success/<pk>/`.

### 5.5. Delivery Assignment & Real-Time Tracking
1. Admin assigns a verified `DeliveryAgentProfile` through the operations panel or Django admin.
2. The customer navigates to `/orders/<pk>/track/` to view a 4-step progressive timeline:
   - Order Placed & Verified
   - Inventory Packed & Sealed
   - Out for Delivery (Rider dispatched)
   - Delivered to Doorstep
3. The delivery agent updates location and notes, which appear on the customer tracking timeline.

### 5.6. Verified Reviews & Rating Feedback
1. Once an order's status reaches `delivered`, a "Review" button activates beside each line item in `/orders/<pk>/`.
2. Only customers with completed purchases can submit ratings (1 to 5 stars) and feedback photos via `/reviews/create/<order_id>/<product_id>/`.
3. Verified purchase badges attach automatically to authentic testimonials displayed on the homepage and detail pages.

### 5.7. Order Cancellation & Stock Restoral
1. Customers can cancel orders that are in `pending` or `confirmed` status directly from `/orders/<pk>/cancel/`.
2. Upon confirmed cancellation:
   - Order status transitions to `cancelled`.
   - Cancellation reason and timestamp are archived.
   - Inventory quantities are automatically restored to the `ProductService` stock pool.

---

## 6. Feature Implementation Matrix: Production vs. Simulated Sandbox

To provide total architectural clarity, the table below documents the exact implementation status of each system capability:

| Feature Area | Architectural State | Implementation Details |
|---|---|---|
| **User Authentication** | **Production-Ready** | Custom User model, session auth, password hashing via PBKDF2/SHA256, role guards. |
| **Catalog & Stock** | **Production-Ready** | Real-time SQLite/PostgreSQL storage, atomic stock deductions, and low-stock indicators. |
| **Cart System** | **Production-Ready** | Client-side persistent cache with strict server-side price recalculation at checkout. |
| **Checkout Flow** | **Production-Ready** | Atomic database transaction, zone delivery fee resolution, order history generation. |
| **Order Cancellation** | **Production-Ready** | Guarded by order state; restores inventory stock automatically upon cancellation. |
| **Fallback Image Engine** | **Production-Ready** | Model-level `.image_url` property backed by 9 inline SVG category illustrations. |
| **Cash on Delivery (COD)**| **Production-Ready** | Full transactional reconciliation and invoice printing support. |
| **Digital Wallet Payments**| **Sandbox / Simulated** | Simulated transaction IDs and payment gateway callbacks for bKash, Nagad, and Card. |
| **Delivery Agent GPS** | **Sandbox / Simulated** | Driver location logs and updates work via database models; live WebSockets / map SDKs are planned. |
| **Email / SMS Dispatch** | **Development Engine** | Configured to use Django console / SMTP backend; external Twilio/SendGrid APIs are external integrations. |

---

## 7. Frontend Design System, Component Library & UX Patterns

### 7.1. Color Palette & Typography
* **Primary Deep Navy:** `#0f172a` (Header, hero sections, primary cards)
* **Electric Accent Blue:** `#0284c7` / `#0ea5e9` (Buttons, highlights, active states)
* **Light Slate Surface:** `#f8fafc` / `#f1f5f9` (Backgrounds, table headers, containers)
* **Status Indicators:**
  * Emerald Green (`#10b981`): In Stock, Delivered, Success
  * Amber Orange (`#f59e0b`): Pending, Low Stock, Warning
  * Crimson Red (`#ef4444`): Out of Stock, Cancelled, Errors
* **Typography:** Modern clean sans-serif typography using system font stacks and `Plus Jakarta Sans`.

### 7.2. Core UI Components
1. **`.sd-product-card`**: Modern card with image frame, category pill, stock level status, title, price in BDT (৳), and one-click cart trigger.
2. **`.badge-status`**: Standardized status badges reflecting order life-cycle (`status-pending`, `status-confirmed`, `status-delivered`, `status-cancelled`).
3. **`.sd-table`**: Clean responsive data tables featuring alternating highlights and mobile horizontal scrolling containers.
4. **Toast Alerts**: Built-in Django messaging rendered through Bootstrap toast alerts with auto-dismiss timers.

---

## 8. Static Assets, Category Fallbacks & Media Pipeline

### 8.1. Fallback Image Strategy
To ensure that products without dedicated uploaded photography never render broken placeholder boxes or distorted layouts, SwiftDrop implements a dual-tier image strategy:
1. **Model Property:** `ProductService.image_url` inspects `self.image`. If valid and present on disk, it returns `self.image.url`.
2. **Category Fallback Vector:** If absent or blank, it returns `/static/images/fallbacks/<category>.svg`.
3. **Client-Side Graceful Degradation:** All `<img>` tags include `onerror="this.onerror=null; this.src='/static/images/fallbacks/default.svg';"` to catch any runtime file system failures gracefully.

Supported category vectors in `static/images/fallbacks/`:
* `food.svg`, `groceries.svg`, `medicine.svg`, `gas.svg`, `electronics.svg`, `documents.svg`, `clothing.svg`, `books.svg`, `default.svg`.

---

## 9. Forms, Validation Rules & Server-Side Integrity

All user inputs are validated through Django ModelForms and custom clean methods:
* **`UserRegistrationForm`**: Enforces minimum password strength, matching confirmation, unique email existence, and valid Bangladeshi phone number regex (`^\+?8801[3-9]\d{8}$`).
* **`OrderCancellationForm`**: Validates that cancellation reason is selected and requires explicit customer confirmation.
* **`CheckoutForm`**: Enforces full delivery street address, recipient contact number, and recognized delivery zone.
* **`ReviewForm`**: Enforces rating integer boundaries between 1 and 5 and sanitizes text comment input.

---

## 10. Security Engineering & Authentication Framework

1. **CSRF Protection:** Every state-mutating form and AJAX endpoint requires a valid `{% csrf_token %}` header/cookie.
2. **SQL Injection Prevention:** 100% of queries leverage the Django ORM parameterization; no raw unescaped SQL queries exist.
3. **Password Security:** Credentials hashed using Django's default PBKDF2 with SHA-256 algorithm with high salt iterations.
4. **Role-Based Access Control (RBAC):**
   - `@login_required` on all customer dashboard, cart checkout, and tracking endpoints.
   - `@user_passes_test(lambda u: u.is_staff or u.user_type == 'admin')` on all administrative interfaces.
   - Object-level ownership validation on order details (`Order.objects.filter(customer=request.user)`).
5. **XSS & Content Sniffing Mitigation:** Production settings activate `SECURE_BROWSER_XSS_FILTER = True`, `SECURE_CONTENT_TYPE_NOSNIFF = True`, and `X_FRAME_OPTIONS = 'DENY'`.

---

## 11. Database Schema, Indexing & Migration History

* **Current Engine:** SQLite 3 for zero-configuration local development.
* **Production Compatibility:** Configured for PostgreSQL (via `psycopg2-binary` or `dj-database-url`).
* **Database Migrations:** All model changes are strictly tracked in version-controlled migration files across `users`, `orders`, `delivery`, `payments`, `reviews`, and `dashboard`.
* **Zero Mojibake / English Cleanliness:** All migration metadata, model verbose names, choice strings, and fixtures have been normalized to professional English.

---

## 12. Automated Testing Suite & Verification Protocol

SwiftDrop includes 25 unit and integration tests verifying every core functional flow:

```bash
# Execute the complete automated test suite
python manage.py test users orders delivery payments reviews dashboard
```

### Verified Test Cases:
* **`users.tests`**: Customer creation, unique phone constraint validation, email authentication backend, profile signals.
* **`orders.tests`**: Catalog listing, category filtering, product detail view, order calculation, stock deduction, order cancellation rules.
* **`delivery.tests`**: DeliveryArea listing, assignment linking, status history progression.
* **`payments.tests`**: Payment method queries, transaction logging, payment detail views.
* **`reviews.tests`**: Verified purchase review creation, star rating range limits.
* **`dashboard.tests`**: Home view rendering, contact form submission, operational metrics view.

---

## 13. Deployment Readiness & Production Configuration

### 13.1. Environment Variables (`.env`)
```ini
DJANGO_SECRET_KEY=your-secure-random-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,127.0.0.1
DATABASE_URL=postgres://user:password@hostname:5432/swiftdrop_db
EMAIL_HOST_USER=rifat5566123@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

### 13.2. Static Asset Collection & WSGI
```bash
# Collect static files for Nginx / WhiteNoise
python manage.py collectstatic --noinput --settings=Nagaribashi_express.settings_production

# Start production application server
gunicorn Nagaribashi_express.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## 14. Local Development & Demo Credentials

To run SwiftDrop locally for evaluation and grading:

```bash
# 1. Activate Python virtual environment
.\.venv\Scripts\activate

# 2. Apply database migrations
python manage.py migrate

# 3. Seed demo accounts & sample catalog
python manage.py setup_data

# 4. Start local development server
python manage.py runserver
```

### Pre-Configured Demo Credentials:
* **Customer Account:**
  * **Email:** `rifat@gmail.com`
  * **Password:** `123456`
  * **Role:** Standard customer (Browsing, cart, checkout, order tracking, reviews)
* **Admin Account:**
  * **Email:** `rifatadmin@gmail.com`
  * **Password:** `123456`
  * **Role:** Platform Superuser & Administrator (Inventory control, operations desk, user management)

---

## 15. Future Roadmap & Enterprise Hardening Recommendations

1. **Production Payment Gateway Integration:** Implement live webhook-verified SSLCommerz, bKash Merchant API, or Stripe checkout sessions.
2. **Real-Time Driver Tracking:** Integrate Django Channels with Redis to stream live GPS coordinates from delivery agent devices to a Leaflet/Mapbox customer UI.
3. **SMS Gateway:** Connect Twilio or local SMS aggregator for OTP customer verification and out-for-delivery alerts.
4. **Automated Celery Task Queue:** Offload invoice PDF rendering, email dispatch, and stock alerts to background workers.
5. **Caching Layer:** Implement Redis caching on catalog views (`ProductServiceListView`) to handle high-concurrency flash sales.

---

*© 2026 SwiftDrop. All rights reserved. Developed by [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/).*
