# SwiftDrop — Architectural Solutions & Design Rationale Guide

> **Tagline:** Your Essentials. Delivered Smarter.  
> **Repository:** [https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp](https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp)  
> **Author & Developer:** [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/)  
> **Contact Email:** [rifat5566123@gmail.com](mailto:rifat5566123@gmail.com)

---

## 1. Architectural Challenge & Design Solutions

When developing a hyperlocal on-demand delivery platform, real-world constraints such as network latency, inventory race conditions, broken client-side pricing, and missing product photography present substantial operational hurdles. This document outlines how SwiftDrop strategically solves each challenge.

---

## 2. Key Engineering Solutions

### 2.1. Challenge: Client-Side Price Tampering
* **The Problem:** In many web applications, shopping carts calculate line item totals and send the total amount directly to the server, allowing malicious users to alter prices using browser developer tools.
* **The SwiftDrop Solution:** The client application strictly maintains an ephemeral representation of item IDs and desired quantities in `localStorage`. When checkout is submitted to `/orders/checkout/`, Django discards any client-sent price and performs an authoritative database lookup against `ProductService.objects.filter(id__in=ids)`. The true total is calculated server-side within an atomic transaction.

### 2.2. Challenge: Inventory Race Conditions & Overselling
* **The Problem:** Multiple customers checking out simultaneously could purchase the last remaining unit of high-demand items (e.g., LPG gas or emergency medicine).
* **The SwiftDrop Solution:** SwiftDrop leverages `transaction.atomic()` during order placement. Stock quantities are verified immediately before order commitment. If `product.stock_quantity < requested_quantity`, an exception aborts the checkout and notifies the customer, preventing negative inventory.

### 2.3. Challenge: Broken Images & Inconsistent Card Layouts
* **The Problem:** When products are uploaded without images or when images fail to load from storage, product grids render unsightly broken image icons or collapsed card layouts.
* **The SwiftDrop Solution:** Dual-tier image fallback:
  1. **Model Property:** `ProductService.image_url` dynamically checks if `self.image` is valid on disk. If absent, it automatically serves a curated category-specific SVG vector illustration (`/static/images/fallbacks/<category>.svg`).
  2. **Client-Side Guard:** All `<img>` tags implement `onerror="this.onerror=null; this.src='{% static 'images/fallbacks/default.svg' %}';"` to gracefully handle 404s or network drops.

### 2.4. Challenge: Email-Based Authentication with Legacy Compatibility
* **The Problem:** Standard Django defaults to username-based authentication, whereas modern users expect to log in with their email address.
* **The SwiftDrop Solution:** A custom authentication backend `EmailOrUsernameModelBackend` is registered in `Nagaribashi_express.settings`. It attempts to authenticate credentials against `email` first, then falls back to `username`, providing full flexibility.

### 2.5. Challenge: Order Cancellation with Automated Stock Restoral
* **The Problem:** When an order is cancelled, stock must be returned to inventory reliably without manual staff intervention.
* **The SwiftDrop Solution:** The `OrderCancellationView` checks if `order.status` is in `['pending', 'confirmed']`. Upon customer confirmation:
  - The order status transitions to `cancelled`.
  - For each `OrderItem` in `order.items.all()`, the line item quantity is added back to `item.product.stock_quantity`.
  - An entry is recorded in `OrderStatusHistory` for auditing.

---

## 3. Technology Stack Justification

| Technology | Rationale for Selection |
|---|---|
| **Django 5.2** | Mature ORM, built-in CSRF/XSS security, powerful admin interface, modular app design. |
| **Python 3.13** | Enhanced performance, improved error tracebacks, long-term support. |
| **SQLite (Dev) / PostgreSQL (Prod)** | Zero-configuration local setup; seamless migration to managed cloud databases. |
| **Bootstrap 5.3 + Vanilla JS** | Lightweight, responsive, eliminates heavy frontend framework overhead while delivering snappy UI performance. |

---

*© 2026 SwiftDrop. All rights reserved. Developed by [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/).*
