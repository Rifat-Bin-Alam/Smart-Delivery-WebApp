# SwiftDrop — Your Essentials. Delivered Smarter
[![Django 5.2](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Bootstrap 5.3](https://img.shields.io/badge/Bootstrap-5.3-7952B2?style=for-the-badge&logo=bootstrap)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

**SwiftDrop** is an on-demand hyperlocal essentials delivery platform engineered with **Django**, **Bootstrap 5**, and **JavaScript**. Developed to solve the logistical challenges of rapid urban fulfillment in Bangladesh, SwiftDrop enables customers to order daily groceries, cooked meals, pharmacy items, emergency LPG cooking gas cylinders, and personal parcels with instant cart recalculation, real-time status tracking, verified reviews, and transparent BDT (৳) pricing.

* **Repository:** [https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp](https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp)
* **Author & Developer:** [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/)
* **Contact:** [rifat5566123@gmail.com](mailto:rifat5566123@gmail.com)

---

## ⚡ Key Features by User Role

### 🛍️ Customer Experience
* **Essentials Catalog:** High-priority categories for Fresh Food, Daily Groceries, Pharmaceuticals, LPG Cooking Gas, Electronics, and Documents.
* **Smart Filter & Search:** Instant search filter across title and category with dynamic fallback cards.
* **Persistent Cart System:** Client-side cache in `localStorage` backed by strict server-side price recalculation at checkout.
* **Secure Checkout Flow:** Atomic order creation, zone-based delivery fee computation, and address validation.
* **Visual Status Tracker:** 4-step progressive timeline (`Placed & Verified` → `Packed & Sealed` → `Out for Delivery` → `Delivered`).
* **Verified Customer Reviews:** Star rating (1-5), review comments, and verified purchase badges.
* **Self-Service Cancellation:** Cancellation flow for `pending`/`confirmed` orders with automatic stock restoral.

### 🚴 Delivery Agent Portal
* **Dedicated Courier Hub:** Protected portal for couriers (`/delivery/`).
* **Duty Status Toggle:** Switch active availability state for automated dispatcher assignments.
* **Task Management:** Real-time assignment cards with pickup addresses, customer phone numbers, and delivery instructions.
* **Delivery Status Logs:** Real-time checkpoint updates (`Picked Up` → `On The Way` → `Delivered`).

### 🛡️ Operations Control Center (Admin & Staff)
* **Live Operations Deck (`/dashboard/admin/`):** Real-time aggregation of completed orders, pending volumes, and active agents.
* **Catalog Management (`/orders/admin/`):** Add, update, and manage inventory stock levels with automated low-stock warnings.
* **Order Dispatch & Invoicing:** View and update order statuses, assign couriers, and generate printable PDF invoices.
* **Review Moderation (`/reviews/admin/`):** Moderate customer reviews and provide official merchant responses.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
|---|---|---|
| **Backend Framework** | Django 5.2 | High-level Python Web Framework (MTV Architecture) |
| **Runtime Engine** | Python 3.13 | Verified compatibility with modern typing and performance |
| **Database** | SQLite 3 / PostgreSQL | ACID-compliant relational storage with ORM parameterization |
| **Frontend Styling** | Bootstrap 5.3 + CSS3 | Deep Navy (`#0F172A`) & Electric Blue (`#0284C7`) Design System |
| **Icons & Assets** | FontAwesome 6 + SVG | Custom vector branding and 9 category fallback SVG illustrations |
| **Client Scripting** | Vanilla JavaScript (ES6) | Reactive cart engine, real-time DOM updates, toast notifications |

---

## 🏛️ Architecture Highlights

1. **Custom User Authentication:** Extends `AbstractUser` to support email authentication (`EmailOrUsernameModelBackend`), unique phone numbers, and specialized profiles (`CustomerProfile`, `DeliveryAgentProfile`).
2. **Decoupled Cart & Server Verification:** Cart items are cached in the client's browser for instantaneous interaction. Upon submitting checkout, Django queries the database directly to prevent client-side price tampering.
3. **Graceful Fallback Image Pipeline:** Custom `image_url` property on `ProductService` returns uploaded photography if present, or dynamically routes to category-specific vector SVGs (`static/images/fallbacks/`). All image tags feature client-side `onerror` fallbacks to eliminate broken image icons.
4. **100% English-Only Interface:** Complete elimination of foreign or corrupted text across public customer portals, admin consoles, forms, and database fixtures.

---

## 🔐 Local Development Credentials

SwiftDrop comes pre-seeded with two dedicated demo accounts for local testing and evaluation:

| Account Type | Email Address | Password | Permissions & Role |
|:---|:---|:---|:---|
| **Customer** | `rifat@gmail.com` | `123456` | Standard customer ordering, cart checkout, tracking & reviews |
| **Admin** | `rifatadmin@gmail.com` | `123456` | Full Django superuser, staff portal, inventory & operations control |

> **Quick-Fill Feature:** On the login page (`/users/login/`), click either the **"Customer"** or **"Admin"** helper badge to auto-populate credentials instantly.

---

## 🚀 Step-by-Step Local Setup

### 1. Prerequisites
* Python 3.10+ (Python 3.13 recommended)
* Git installed
* PowerShell / Terminal

### 2. Clone Repository
```bash
git clone https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp.git
cd Smart-Delivery-WebApp
```

### 3. Create & Activate Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations
```bash
python manage.py migrate
```

### 6. Seed Demo Accounts & Catalog
```bash
python manage.py setup_data
```

### 7. Run Local Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Automated Testing Suite

SwiftDrop includes 25 unit and integration tests verifying every critical flow:
```bash
# Run all application test suites
python manage.py test users orders delivery payments reviews dashboard
```

Test coverage includes:
* Email-based customer authentication & profile signals
* Dynamic catalog listing and category filtering
* Tamper-proof price recalculation and stock deduction
* Delivery zone fee lookup and assignment linking
* Payment transaction logging and refund records
* Order cancellation state rules and stock restoral

---

## 📂 Project Structure

```
Smart-Delivery-WebApp/
├── dashboard/               # Operational control, landing page, metrics & FAQs
├── users/                   # Custom User model, auth backend, customer/agent profiles
├── orders/                  # Catalog, cart, checkout, order state machine & tracking
├── delivery/                # Driver dispatch, zones, and fulfillment status logs
├── payments/                # Ledger, simulated transaction logging, and refunds
├── reviews/                 # Verified purchase reviews, star ratings & moderation
├── templates/               # Modular HTML5 templates with clean component hierarchy
├── static/                  # Design system: styles.css, main.js, fallback SVG icons
├── media/                   # Uploaded media assets (product images, avatars)
├── Nagaribashi_express/     # Django settings, WSGI/ASGI, root URL routing
├── requirements.txt         # Pinned Python dependencies (Django 5.2, Pillow, etc.)
├── .env.example             # Safe environment variable configuration template
├── manage.py                # Django management executable
└── README.md                # Project documentation
```

---

## 🌐 Production Deployment Summary

For production deployment (Render, Railway, VPS, PythonAnywhere):
1. Configure environment variables in `.env` based on `.env.example`.
2. Set `DJANGO_DEBUG=False` and configure `DJANGO_ALLOWED_HOSTS`.
3. Collect static files:
   ```bash
   python manage.py collectstatic --noinput --settings=Nagaribashi_express.settings_production
   ```
4. Run WSGI server via Gunicorn:
   ```bash
   gunicorn Nagaribashi_express.wsgi:application --bind 0.0.0.0:8000
   ```
Detailed deployment instructions are documented in [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

---

## 🖼️ User Interface Preview

```
+--------------------------------------------------------------------------+
|  SwiftDrop  [Essentials]  [Categories]  [Track Order]     [Cart (2)] [Rifat]  |
+--------------------------------------------------------------------------+
|                                                                          |
|   Your Essentials. Delivered Smarter.                                    |
|   30-minute hyperlocal delivery across your city.                        |
|                                                                          |
|   [ Fresh Food ]   [ Groceries ]   [ Pharmacy ]   [ LPG Gas Refill ]     |
|                                                                          |
+--------------------------------------------------------------------------+
|  Featured Essentials:                                                    |
|  +-------------------+  +-------------------+  +-------------------+     |
|  | [Food SVG / Photo]|  | [Gas SVG / Photo] |  | [Med SVG / Photo] |     |
|  | Chicken Biryani   |  | LPG Gas (12kg)    |  | Paracetamol 500mg |     |
|  | ৳ 280.00          |  | ৳ 1,350.00        |  | ৳ 25.00           |     |
|  | [ Add to Cart ]   |  | [ Add to Cart ]   |  | [ Add to Cart ]   |     |
|  +-------------------+  +-------------------+  +-------------------+     |
+--------------------------------------------------------------------------+
```

---

## 📄 Authorship, Copyright & Attribution

* **Developed by:** [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/)
* **Portfolio:** [https://rifat-bin-alam.vercel.app/](https://rifat-bin-alam.vercel.app/)
* **GitHub Repository:** [https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp](https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp)
* **Contact Email:** [rifat5566123@gmail.com](mailto:rifat5566123@gmail.com)
* **License:** [MIT License](LICENSE)

*© 2026 SwiftDrop. All rights reserved. Developed by Rifat Bin Alam.*
