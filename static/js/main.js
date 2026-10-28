/**
 * SwiftDrop — Modern Delivery Client-Side Application Script
 */

// Initialize Cart System
const SwiftDropCart = {
  STORAGE_KEY: 'swiftdrop_cart_v1',

  getItems() {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Failed to parse cart data:', e);
      return [];
    }
  },

  saveItems(items) {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(items));
      this.updateBadges();
      window.dispatchEvent(new CustomEvent('swiftdrop:cart-updated', { detail: { items } }));
    } catch (e) {
      console.error('Failed to save cart items:', e);
    }
  },

  addItem(product) {
    let items = this.getItems();
    const existingIndex = items.findIndex(i => String(i.id) === String(product.id));

    if (existingIndex > -1) {
      const maxStock = product.max_stock || 999;
      const newQty = items[existingIndex].quantity + (product.quantity || 1);
      if (newQty > maxStock) {
        showToast(`Only ${maxStock} items available in stock.`, 'error');
        return false;
      }
      items[existingIndex].quantity = newQty;
    } else {
      items.push({
        id: product.id,
        name: product.name,
        price: parseFloat(product.price) || 0,
        quantity: parseInt(product.quantity) || 1,
        image: product.image || '',
        category: product.category || 'essentials',
        max_stock: product.max_stock || 999
      });
    }

    this.saveItems(items);
    showToast(`Added "${product.name}" to cart.`, 'success');
    return true;
  },

  updateQuantity(productId, quantity) {
    let items = this.getItems();
    const itemIndex = items.findIndex(i => String(i.id) === String(productId));

    if (itemIndex > -1) {
      const targetQty = parseInt(quantity);
      if (targetQty <= 0) {
        this.removeItem(productId);
        return;
      }
      const maxStock = items[itemIndex].max_stock || 999;
      if (targetQty > maxStock) {
        showToast(`Stock limit reached (${maxStock} max).`, 'error');
        items[itemIndex].quantity = maxStock;
      } else {
        items[itemIndex].quantity = targetQty;
      }
      this.saveItems(items);
    }
  },

  removeItem(productId) {
    let items = this.getItems().filter(i => String(i.id) !== String(productId));
    this.saveItems(items);
    showToast('Item removed from cart.', 'info');
  },

  clear() {
    localStorage.removeItem(this.STORAGE_KEY);
    this.updateBadges();
    window.dispatchEvent(new CustomEvent('swiftdrop:cart-updated', { detail: { items: [] } }));
  },

  getTotalCount() {
    return this.getItems().reduce((sum, item) => sum + (parseInt(item.quantity) || 0), 0);
  },

  getSubtotal() {
    return this.getItems().reduce((sum, item) => {
      const price = parseFloat(item.price) || 0;
      const qty = parseInt(item.quantity) || 0;
      return sum + (price * qty);
    }, 0);
  },

  updateBadges() {
    const totalCount = this.getTotalCount();
    const badges = document.querySelectorAll('.cart-badge-count');
    badges.forEach(badge => {
      badge.textContent = totalCount;
      badge.style.display = totalCount > 0 ? 'inline-flex' : 'none';
    });
  }
};

// Global Toast System
function showToast(message, type = 'info') {
  let container = document.querySelector('.sd-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'sd-toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `sd-toast ${type}`;

  let icon = '<i class="fas fa-info-circle text-info"></i>';
  if (type === 'success') icon = '<i class="fas fa-check-circle text-success"></i>';
  if (type === 'error') icon = '<i class="fas fa-exclamation-circle text-danger"></i>';

  toast.innerHTML = `
    ${icon}
    <div class="flex-grow-1">${message}</div>
    <button type="button" class="btn-close btn-close-white ms-2" style="font-size: 0.75rem;"></button>
  `;

  toast.querySelector('.btn-close').addEventListener('click', () => toast.remove());
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// CSRF Token Helper
function getCsrfToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];
  if (cookieValue) return cookieValue;
  const tokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
  return tokenInput ? tokenInput.value : '';
}

// Format Currency
function formatBDT(amount) {
  const num = parseFloat(amount) || 0;
  return '৳ ' + num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
  SwiftDropCart.updateBadges();

  // Listen for storage changes across tabs
  window.addEventListener('storage', (e) => {
    if (e.key === SwiftDropCart.STORAGE_KEY) {
      SwiftDropCart.updateBadges();
      window.dispatchEvent(new CustomEvent('swiftdrop:cart-updated', {
        detail: { items: SwiftDropCart.getItems() }
      }));
    }
  });

  // Attach Add-To-Cart buttons
  document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const card = btn.closest('[data-product-id]');
      const product = {
        id: btn.dataset.productId || (card && card.dataset.productId),
        name: btn.dataset.productName || (card && card.dataset.productName),
        price: btn.dataset.productPrice || (card && card.dataset.productPrice),
        image: btn.dataset.productImage || (card && card.dataset.productImage),
        max_stock: parseInt(btn.dataset.productStock || (card && card.dataset.productStock) || 999),
        quantity: 1
      };
      if (product.id && product.name) {
        SwiftDropCart.addItem(product);
      }
    });
  });
});
