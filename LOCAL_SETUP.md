# SwiftDrop — Windows Local Development Guide

This guide walks you through setting up, running, testing, and troubleshooting **SwiftDrop** on Windows 10/11 using PowerShell and Visual Studio Code.

---

## 📋 System Prerequisites
- **Python:** 3.10 to 3.13 (Python 3.13.14 verified)
- **PowerShell:** Default Windows PowerShell 5.1 or PowerShell 7+
- **VS Code:** Recommended editor

---

## ⚡ 1-Minute Quick Start

Open PowerShell inside the project directory:
```powershell
cd "f:\IUBAT\8th Semester\CSE 3391\Smart Delivery Webapp\Smart-Delivery-WebApp"
```

### 1. Activate the Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```
*(If you see an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### 2. Verify Database & Migrations
```powershell
python manage.py migrate
```

### 3. Seed Demo Accounts
```powershell
python manage.py seed_demo_accounts
```

### 4. Run the Development Server
```powershell
python manage.py runserver
```
Navigate to: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Login Accounts for Testing

SwiftDrop includes one-click credentials auto-fill on the sign-in page (`/users/login/`):

1. **Customer Account**
   - **Email:** `rifat@gmail.com`
   - **Password:** `123456`
   - **Role:** Regular Customer (browses catalog, adds to cart, places orders, tracks live deliveries, submits reviews).

2. **Administrator Account**
   - **Email:** `rifatadmin@gmail.com`
   - **Password:** `123456`
   - **Role:** Staff & Superuser (accesses Operations Control Center, assigns delivery couriers, moderates reviews, manages inventory stock, updates zone pricing).

3. **Delivery Partner Account**
   - **Email:** `agent@swiftdrop.com`
   - **Password:** `123456`
   - **Role:** Courier / Rider (logs in to `/delivery/`, toggles duty availability, accepts and marks orders as picked up, in-transit, and delivered).

---

## 🧪 Running the Automated Test Suite

To run all 18 automated unit tests:
```powershell
python manage.py test
```

Expected output:
```
Ran 18 tests in ~40s
OK
```

---

## 🔧 Common Troubleshooting & FAQs

### Q: "sqlite3.OperationalError: database is locked"
**Cause:** You have `db.sqlite3` open in a GUI tool such as **DB Browser for SQLite** or **DBeaver** with an open write transaction.
**Fix:**
1. In *DB Browser for SQLite*, click **"Write Changes"** or **"Close Database"**.
2. Or simply close the *DB Browser for SQLite* window.
3. Then retry your `python manage.py runserver` or `migrate`.

### Q: "No directory at ... staticfiles"
This is a standard informational warning from Django's `WhiteNoise` middleware when static collection has not been executed locally. It does not affect local development because Django serves static files directly from `static/`.

### Q: How do I test Cash on Delivery (COD) vs Digital Wallet?
1. Log in as `rifat@gmail.com`.
2. Browse items at `/orders/products/` and click **"Add to Cart"**.
3. Go to `/orders/cart/` and proceed to **Checkout**.
4. Select your delivery zone (e.g., *Dhanmondi* or *Uttara*).
5. Choose **Cash on Delivery** or **bKash / Nagad / Rocket**.
6. For mobile wallets, input any test Transaction ID (e.g., `TRX-TEST-001`).
7. Complete checkout and monitor live order tracking at `/orders/<id>/track/`.
8. Log in as `agent@swiftdrop.com` to deliver the order, or as `rifatadmin@gmail.com` to manage the fulfillment console.

---

*© 2026 SwiftDrop. All rights reserved. Developed by [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/).*

