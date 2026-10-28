# SwiftDrop — Shopping Cart & Checkout Architecture Guide

> **Tagline:** Your Essentials. Delivered Smarter.  
> **Repository:** [https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp](https://github.com/Rifat-Bin-Alam/Smart-Delivery-WebApp)  
> **Author & Developer:** [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/)  
> **Contact Email:** [rifat5566123@gmail.com](mailto:rifat5566123@gmail.com)

---

## 1. Overview of the Cart System

SwiftDrop incorporates a high-performance, hybrid shopping cart architecture:
* **Client-Side Persistence:** Fast, reactive cart actions (add, increment, decrement, remove, clear) stored in browser `localStorage`.
* **Cross-Tab Synchronization:** Custom JavaScript events (`swiftdrop:cart-updated`) keep cart counts and totals synchronized across multiple tabs and components.
* **Server-Side Integrity & Tamper-Proofing:** While the client presents an interactive estimation of the total, the final checkout execution queries actual product records in the database to prevent client-side price tampering.

---

## 2. Client-Side Cart Engine (`SwiftDropCart`)

The cart engine is defined in `static/js/main.js` as an encapsulated singleton object attached to `window.SwiftDropCart`:

### 2.1. Cart Data Structure
Items are stored in `localStorage` under the key `'swiftdrop_cart'`:
```json
[
  {
    "id": 1,
    "name": "Chicken Biryani Special",
    "price": 280.00,
    "image": "/media/products/mutton-biriyani-recipe.jpeg",
    "quantity": 2
  }
]
```

### 2.2. Core API Methods

| Method | Parameters | Description |
|---|---|---|
| `SwiftDropCart.getItems()` | None | Returns array of current cart items from `localStorage`. |
| `SwiftDropCart.addItem(item)` | `{ id, name, price, image, quantity }` | Appends new item or increments quantity if item already exists. |
| `SwiftDropCart.updateQuantity(id, qty)`| `(id, quantity)` | Sets specific item quantity. If `qty <= 0`, item is removed. |
| `SwiftDropCart.removeItem(id)` | `(id)` | Removes item matching `id` from the cart. |
| `SwiftDropCart.clear()` | None | Clears the cart array from `localStorage`. |
| `SwiftDropCart.getCount()` | None | Returns the total sum of item quantities. |
| `SwiftDropCart.getSubtotal()` | None | Returns calculated subtotal (`price * quantity`). |

### 2.3. Event-Driven UI Updates
Whenever any cart mutation occurs, `SwiftDropCart` dispatches a global window event:
```javascript
window.dispatchEvent(new CustomEvent('swiftdrop:cart-updated', { detail: { count, subtotal } }));
```
All UI elements (navbar counter badge, sidebar summary, cart item tables) listen for this event and update reactively.

---

## 3. Server-Side Verification & Checkout Flow

### 3.1. Checkout Initiation (`/orders/checkout/`)
When the customer navigates to the checkout page:
1. The client-side cart items are converted to a hidden form field or passed via JSON payload.
2. The customer provides:
   - Full delivery street address
   - Recipient phone number
   - Delivery city & area zone
   - Special delivery notes
   - Payment method (Cash on Delivery, bKash, Nagad, Card)

### 3.2. Tamper-Proof Order Placement (`create_order_from_cart`)
1. **Price Verification:** Django iterates through the submitted product IDs and queries `ProductService.objects.filter(id__in=ids)`.
2. **True Calculation:** Unit prices are derived from `product.price` in the database, NOT from client-submitted data.
3. **Stock Verification:** The system checks that `product.stock_quantity >= requested_quantity`.
4. **Zone Fee Resolution:** Delivery fee is verified against the selected `DeliveryArea`.
5. **Atomic Transaction:** The order, order items, and stock deductions are executed in a single atomic database block:
   ```python
   with transaction.atomic():
       order = Order.objects.create(...)
       for item in validated_items:
           OrderItem.objects.create(...)
           product.stock_quantity -= item['qty']
           product.save()
   ```
6. **Cart Clearing:** Once the order is committed to the database, the client's `localStorage` cart is cleared and the customer is redirected to `/orders/success/<order_id>/`.

---

## 4. Edge Cases & Resilience Mechanisms

* **Empty Cart Guard:** Checkout cannot be submitted with 0 items; UI disables the submit button and displays a helpful empty state with a "Browse Essentials" button.
* **Out of Stock During Checkout:** If another customer purchases remaining stock before checkout completes, the server rejects the order with a clear warning, preventing overselling.
* **Fallback Images in Cart:** Cart item rows feature `onerror` fallback handling, ensuring missing uploaded photos fall back gracefully to `/static/images/fallbacks/default.svg`.

---

*© 2026 SwiftDrop. All rights reserved. Developed by [Rifat Bin Alam](https://rifat-bin-alam.vercel.app/).*
