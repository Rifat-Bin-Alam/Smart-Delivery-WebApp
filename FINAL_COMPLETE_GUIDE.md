# SwiftDrop — Complete Operations & Developer Manual

> **Tagline:** Your Essentials. Delivered Smarter.  
> **Repository:** [https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp](https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp)  
> **Author & Developer:** [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/)  
> **Contact Email:** [rifat5566123@gmail.com](mailto:rifat5566123@gmail.com)

---

## 1. Executive Overview

**SwiftDrop** is a full-featured on-demand delivery web platform designed for rapid metropolitan dispatch. It connects customers seeking high-priority essentials (cooked meals, pharmaceuticals, cooking gas, and groceries) with logistics dispatchers and couriers.

---

## 2. Complete Platform Sitemap & Route Directory

| Module | URL Endpoint | Description | Access Level |
|---|---|---|---|
| **Home** | `/` | Main landing page, hero search, metrics & features | Public |
| **Catalog** | `/orders/products/` | Interactive catalog with category filters & cart integration | Public |
| **Product Detail** | `/orders/product/<pk>/` | Detailed view, stock availability, specifications | Public |
| **Cart** | `/orders/cart/` | Review selected items, adjust quantities, fee estimate | Public |
| **Checkout** | `/orders/checkout/` | Address entry, delivery zone selection, order creation | Authenticated |
| **Order History** | `/orders/` | List of customer's previous orders & current statuses | Authenticated |
| **Order Detail** | `/orders/<pk>/` | Itemized order breakdown, invoice link, cancellation trigger | Authenticated |
| **Live Tracking** | `/orders/<pk>/track/` | 4-step progressive timeline tracking fulfillment | Authenticated |
| **Invoice** | `/orders/invoice/<order_number>/` | Printable official billing receipt | Authenticated |
| **Cancel Order** | `/orders/<pk>/cancel/` | Customer cancellation with reason and stock restoral | Authenticated |
| **Customer Hub** | `/users/dashboard/` | Account overview, active orders, saved addresses | Authenticated |
| **Courier Hub** | `/delivery/` | Delivery agent duty toggle, assigned deliveries, status logs | Delivery Agent |
| **Operations Hub**| `/dashboard/admin/` | High-level analytics, pending deliveries, fleet overview | Staff / Admin |
| **Admin Catalog** | `/orders/admin/` | Inventory management, order status update tools | Staff / Admin |
| **Review Moderation**| `/reviews/admin/` | Moderation queue for submitted customer ratings | Staff / Admin |
| **Django Admin** | `/admin/` | Comprehensive low-level ORM administration portal | Superuser |

---

## 3. Pre-Configured Demo Accounts

For local evaluation, grading, and testing:

| Role | Email Address | Password | Functionality |
|---|---|---|---|
| **Customer** | `rifat@gmail.com` | `123456` | Catalog shopping, cart management, checkout, live tracking, reviews, order cancellation |
| **Administrator** | `rifatadmin@gmail.com` | `123456` | Full platform control, inventory management, fleet management, operations metrics |

---

## 4. Customer User Guide

### 4.1. Selecting Essentials
1. Browse categories from the homepage or go directly to `/orders/products/`.
2. Filter by category pills (Food, Medicine, Gas, Groceries, Electronics, Books).
3. Click "Add to Cart" to immediately append the item to your active session.

### 4.2. Checkout & Order Finalization
1. Navigate to `/orders/cart/` to verify items and quantities.
2. Click "Proceed to Checkout" (`/orders/checkout/`).
3. Enter your street address, select your delivery area, and choose a payment method.
4. Click "Confirm & Place Order". The order is created atomically and inventory is reserved.

### 4.3. Tracking & Receipts
1. Immediately upon ordering, click "Track Order" or visit `/orders/<pk>/track/`.
2. Access your printable PDF/HTML invoice via `/orders/invoice/<order_number>/`.

### 4.4. Ratings & Feedback
Once your order status changes to `delivered`, click the "Review" button on your order details page to submit a 1 to 5 star rating with feedback.

---

## 5. Operations & Administration Guide

1. Log in with `rifatadmin@gmail.com`.
2. Access the **Operations Control Center** at `/dashboard/admin/` or via the top navigation bar.
3. Use the **Inventory Hub** (`/orders/admin/`) to monitor stock levels. Items with stock $\le 5$ are highlighted with low-stock badges.
4. To assign an agent to an order, navigate to `/delivery/assignments/` and select a verified rider.

---

*© 2026 SwiftDrop. All rights reserved. Developed by [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/).*
